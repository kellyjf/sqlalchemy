#!/usr/bin/python3


import requests
from lxml import html
import sqlite3
from schema import Synonym,Definition,Category,Statistic, Subject, Verb, Tense, Conjugation, Sentence, Rule, State, Base, init
import os.path
import re

from sqlalchemy import create_engine, not_
engine=create_engine("sqlite:///portuguese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)


# verb - lookup key onweb and file name
# infinitivo -infinitive form of the verb, for text output and database keys	
def load_verb(verb):
	verbreg=True
	category=""
	ecats={x.text:x for x in verb.categories}
	if verb.id=="pôr":
		web="por-2"
	else:
		web=verb.id
	if not os.path.exists(f"dic/{web}.txt"):
		r=requests.get(f"https://www.dicio.com.br/{web}/")
		if r.status_code==200:
			with open(f"dic/{web}.txt","wb") as fd:
				fd.write(r.content)

	with open(f"dic/{web}.txt","rb") as fd:
		tree=html.fromstring(fd.read())
		parts=tree.xpath("//p[@class='adicional']")
		for part in parts:
			re1=re.search("Classe gramatical:\s*(.*)\n",part.text_content())
			if re1:
				cat=re1.group(1).replace(" e verbo",", verbo")
				clist=cat.split(",")
				
				for cat in clist:
					text=" ".join(cat.strip().split(" ")[1:])
					session.add(Category(verb_id=verb.id, text=text))
		parts=tree.xpath("//span[@class='cl']")
		for part in parts:
			cat=part.text_content()
			if cat:
				cat=cat.replace("verbo ","")
				cat=cat.replace("substantivo ","")
				cat=cat.replace(" e ",", ").strip()
				for ctype in cat.split(","):
					ctype=ctype.strip()
#					print("CAT",verb.id,ctype)
					if ctype in ecats:
						rescat=ecats.get(ctype)
					else:
						rescat=Category(verb_id=verb.id,text=ctype)
						session.add(rescat)
						session.commit()
			part=part.getnext()
			while part is not None  and 'class' not in part.attrib:
				content=part.text_content()
				if ":" in content:
					[define,example]=content.split(":")[0:2]
				else:
					[define,example]=[content,""]
				define=define.strip()
				example=example.strip()
				session.add(Definition(category_id=rescat.id,text=define,example=example))

				part=part.getnext()

		parts=tree.xpath(".//p[@class='adicional sinonimos']")
		contr=True
		for part in parts:
			contr = not contr
			cat=part.text_content()
			sparts=part.xpath(".//a")
			for tgt in sparts:
				session.add(Synonym(verb_id=verb.id,related_id=tgt.text_content(),contrary=contr))

	session.commit()			


from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--rules-only","-r", action="store_true", help="Only load sentence templates")
	args=parser.parse_args()
	for cat in session.query(Category).all():
		session.delete(cat)
	session.commit()
	for verb in session.query(Verb).filter(not_(Verb.id.like('*%'))).all():
			load_verb(verb)


