#!/usr/bin/python3


import requests
from lxml import html
import sqlite3

#con=sqlite3.connect('fr.sqlite')
#cur=con.cursor()

r=requests.get("https://www.conjugacao.com.br/verbo-querer/")

tensemap = {
	'Indicativo' : {
		'Presente':'ip',
		'Pretérito Imperfeito': 'iri',
		'Pretérito Perfeito': 'irp',
		'Pretérito Mais-que-perfeito': 'irm',	
		'Futuro do Presente': 'if',
		'Futuro do Pretérito': 'cp' },
	'Subjuntivo': {
		'Presente':'sp',
		'Pretérito Imperfeito': 'st',
		'Futuro': 'sf' },
	'Imperativo' : {
		'Imperativo Afirmativo': 'ma',
		'Imperativo Negativo' : 'mn' },
	'Infinitivo': {
		'Infinitivo Pessoal' : 'v' }
	}

		

if r.status_code==200:
	tree=html.fromstring(r.content)
	parts=tree.xpath("//div[@class='info-v']")
	for part in parts:
		pparts=part.xpath(".//span[@class='f']")
		if len(pparts)>1:
			gerund=pparts[0].text
			past_part=pparts[1].text
	modes=tree.xpath("//h3[@class='modoconjuga']")
	print(modes)
	for mode in modes:
		mmap=tensemap.get(mode.text,{})
		tenses=mode.getparent().xpath(".//div[@class='tempo-conjugacao']")
		for tense in tenses:
			tensenames=tense.xpath(".//h4[@class='tempo-conjugacao-titulo']")
			for tn in tensenames:
				tkey=mmap.get(tn.text, None)
			irregs=tense.xpath(".//span[@class='f irregular']")
			for irreg in irregs:
				spans=irreg.getparent().xpath(".//span")
				print(tkey,spans[0].text,spans[1].text)
def junk():
	if False:
		if False:
			irrs=tense.xpath(".//span[@class='f irregular']")
			for irr in irrs:
				for con in irr.getparent().xpath("./span"):
					print(con.text)
#	a=cur.execute("insert into test (pron) values ('Hello')")
#	b=cur.execute("insert into test (pron) values (?)",(val,))
#	print(a,b)
#	cur.close()
#	con.commit()

print(tree)

