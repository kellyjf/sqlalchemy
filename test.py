#!/usr/bin/python3


import requests
from lxml import html
import sqlite3

#con=sqlite3.connect('fr.sqlite')
#cur=con.cursor()

r=requests.get("https://www.conjugacao.com.br/verbo-querer/")


if r.status_code==200:
	tree=html.fromstring(r.content)
	parts=tree.xpath("//div[@class='info-v']")
	for part in parts:
		pparts=part.xpath(".//span[@class='f']")
		for ppart in pparts:
			print("PART:", ppart.text)
	modes=tree.xpath("//h3[@class='modoconjuga']")
	print(modes)
	for mode in modes:
		print("MODO: ", mode.text)
		tenses=mode.getparent().xpath(".//div[@class='tempo-conjugacao']")
		for tense in tenses:
			tensenames=tense.xpath(".//h4[@class='tempo-conjugacao-titulo']")
			for tn in tensenames:
				print("TENSE ", tn.text)
			irregs=tense.xpath(".//span[@class='f irregular']")
			for irreg in irregs:
				spans=irreg.getparent().xpath(".//span")
				print(spans[0].text,spans[1].text)
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

