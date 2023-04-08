#!/usr/bin/python3


import requests
from lxml import html
import sqlite3
from wschema import Duvida,Example,Synonym,Definition,Category, Word, Base
import os.path
import re
import subprocess 

from sqlalchemy import create_engine, not_
engine=create_engine("sqlite:///words.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)



def load_ipa(word):
	wordreg=True
	cmd = ['espeak', '-q', '-v', 'pt-BR', '--ipa', word.id ]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	p.wait()
	word.ipa=p.stdout.read().strip().decode('utf-8')
	session.add(word)

def load_defs(word):
	wordreg=True
	category=""
	ecats={x.text:x for x in word.categories}
	if word.id=="pôr":
		web="por-2"
	else:
		web=word.id
		web=web.replace('â','a')
		web=web.replace('ã','a')
		web=web.replace('á','a')
		web=web.replace('ê','e')
		web=web.replace('é','e')
		web=web.replace('í','i')
		web=web.replace('ô','o')
		web=web.replace('õ','o')
		web=web.replace('ó','o')
		web=web.replace('ú','u')
		web=web.replace('ç','c')
		web=web.replace('-se','')
	if not os.path.exists(f"dic/{web}.txt"):
		r=requests.get(f"https://www.dicio.com.br/{web}/")
		if r.status_code==200:
			with open(f"dic/{web}.txt","wb") as fd:
				fd.write(r.content)

	with open(f"dic/{web}.txt","rb") as fd:

		tree=html.fromstring(fd.read())

		# Gramatical categories
		parts=tree.xpath("//p[@class='adicional']")
		for part in parts:
			if 'Classe gramatical' in part.text:
				for tag, text in [(x.tag,x.text) for x in part.getchildren()]:
					if tag!='b':
						break
					if text not in ecats:
						cat=Category(word_id=word.id,text=text)
						session.add(cat)
						session.commit()
						ecats[text]=cat
			for br in  part.xpath("./br"):
				if br.tail and "Plural" in br.tail:
					word.plural=br.getnext().text_content()

		# Definitions and examples
		parts=tree.xpath("//span[@class='cl']")
		for part in parts:
			cat=part.text_content()
			if cat:
				for ctype in cat.split(","):
					ctype=ctype.strip()
#					print("CAT",word.id,ctype)
					if ctype in ecats:
						rescat=ecats.get(ctype)
					else:
						rescat=Category(word_id=word.id,text=ctype)
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

		# Synonyms and antonyms
		parts=tree.xpath(".//p[@class='adicional sinonimos']")
		contr=True
		for part in parts:
			contr = not contr
			cat=part.text_content()
			sparts=part.xpath(".//a")
			for tgt in sparts:
				session.add(Synonym(word_id=word.id,related_id=tgt.text_content(),contrary=contr))


		# Phrases
		parts=tree.xpath(".//h3[@class='tit-frases']")
		if parts:
			for part in parts[0].getnext().xpath("./div[@class='frase']"):
				for span in part.xpath("./span"):
					text=span.text
					source=""
					for src in span.xpath("./em"):
						source=src.text.replace("- ","")
					session.add(Example(word_id=word.id,text=text,source=source,phrase=True))
						

		#Examples
		parts=tree.xpath(".//h3[@class='tit-exemplo']")
		if parts:
			x=parts[0].getnext()
			for part in parts[0].getnext().xpath("./div[@class='frase']"):
				
				source=""
				for src in part.xpath("./em"):
					source=src.text.replace("- ","")
				text=part.text_content().replace(source,"").strip()
				session.add(Example(word_id=word.id,text=text,source=source,phrase=False))


		#Duvidas
		parts=tree.xpath(".//div[@id='desamb']")
		if parts:
			text=parts[0].text_content()
			vid=parts[0].getnext()
			url=""
			if vid.attrib.get('class','')=="videoWrapper":
				for node in vid.getchildren():
					if node.tag=='iframe' and 'src' in node.attrib:
						url=node.attrib.get('src','-error-')

			session.add(Duvida(word_id=word.id,text=text,url=url))

		load_ipa(word)

	session.commit()			



from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--rules-only","-r", action="store_true", help="Only load sentence templates")
	parser.add_argument("--quiet","-q", action="store_true", help="Operate silently")
	parser.add_argument("--cached","-c", action="store_true", help="Don't use internet")
	parser.add_argument("--words","-w", nargs='*', action='store',  help="Add named words")

	args=parser.parse_args()

	if args.words:
		for wordid in args.words:
			word=session.query(Word).filter(Word.id==wordid).first()
			if word:
				for duv in word.duvidas:
					session.delete(duv)
				for example in word.examples:
					session.delete(example)
				for syn in word.synonyms:
					session.delete(syn)
				for cat in word.categories:
					for defn in cat.definitions:
						session.delete(defn)
					session.delete(cat)
				session.delete(word)
			word=Word(id=wordid)
			session.add(word)
			session.commit()
	
			load_defs(word)
			session.commit()

	else:
		pass

