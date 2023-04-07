#!/usr/bin/python3


import requests
from lxml import html
import sqlite3
from schema import Statistic, Subject, Verb, Tense, Conjugation, Sentence, Rule, State, Base, init
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
				
				rlist=["-".join( [y[:4] for y in x.split()[1:]]) for x in clist]
				verb.category=",".join(rlist)
				session.add(verb)

	session.commit()			


from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--rules-only","-r", action="store_true", help="Only load sentence templates")
	args=parser.parse_args()

	for verb in session.query(Verb).filter(not_(Verb.id.like('*%'))).all():
			load_verb(verb)


