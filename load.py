#!/usr/bin/python3


import requests
from lxml import html
import sqlite3
from schema import Statistic, Subject, Verb, Tense, Conjugation, Sentence, Rule, State, Base, init
import os.path
import re

from sqlalchemy import create_engine
engine=create_engine("sqlite:///portuguese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)


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

personmap = {
	'eu' : '1ps',
	'tu' : '2ps',
	'ele' : '3ps',
	'você' : '3ps',
	'nós' : '1pp',
	'vós' : '2pp',
	'vocês' : '3pp',
	'eles' : '3pp' }

# verb - lookup key onweb and file name
# infinitivo -infinitive form of the verb, for text output and database keys	
def load_verb(verb, infinitivo=""):
	verbreg=True
	category=""
	web=verb
	web=web.replace('ô','o')
	web=web.replace('ç','c')

	if not os.path.exists(f"net/{web}.txt"):
		r=requests.get(f"https://www.conjugacao.com.br/verbo-{web}/")
		if r.status_code==200:
			with open(f"net/{web}.txt","wb") as fd:
				fd.write(r.content)

	if not os.path.exists(f"net/{web}.txt"):
		print(f"FAIL: {verb}/{web}")
		return

	with open(f"net/{web}.txt","rb") as fd:
		tree=html.fromstring(fd.read())
		parts=tree.xpath("//div[@class='info-v']")
		for part in parts:
			pparts=part.xpath(".//span[@class='f']")
			if len(pparts)>1:
				gerund=pparts[0].text
				past_part=pparts[1].text
			pparts=part.xpath(".//p[@class='secondary']")
			if len(pparts)>0:
				tgt=pparts[0].text_content()
				re1=re.search("Transitividade:\s*(.*)\s*Separa",tgt)
				if re1:
					cat=re1.group(1)
					cat=cat.replace(" e  ",",  ")
					types=cat.split(",")
					tlist=[]
					for x in types:
						x=x.strip()
						res="".join([y[0] for y in x.split()])
						if res=="i":
							res="in"
						elif res=="p":
							res="pr"
						elif res=="t":
							res="tr"
						tlist.append(res)
					category=",".join(tlist)
		modes=tree.xpath("//h3[@class='modoconjuga']")
		for mode in modes:
			mkey=mode.text
			mmap=tensemap.get(mkey,{})
			tenses=mode.getparent().xpath(".//div[@class='tempo-conjugacao']")
			for tense in tenses:
				tensenames=tense.xpath(".//h4[@class='tempo-conjugacao-titulo']")
				for tn in tensenames:
					tkey=mmap.get(tn.text, None)
				irregs=tense.xpath(".//span[@class='f irregular']")
				for irreg in irregs:
					verbreg=False
					spans=irreg.getparent().xpath(".//span")
					if tkey in ['mn', 'v']: 
						ptext = spans[2].text
						text = spans[1].text
					elif tkey=='ma': 
						ptext = spans[1].text
						text = spans[0].text
					else:
						ptext = spans[0].text
						text = spans[1].text
					pid=ptext.split(" ")[-1]
					person=personmap.get(pid,"False")
					if person:
						session.add(Conjugation(verb_id=verb, tense_id=tkey, person=person, text=text))
		session.add(Verb(id=infinitivo, regular=verbreg, gerund=gerund, past_part=past_part))

def load_db():

	# Subjects
	session.add(Subject(person="1ps", reflex='me',text="eu"))
	session.add(Subject(person="1pp", reflex='me', text="nós"))
	session.add(Subject(person="3ps", reflex='se', text="ele"))
	session.add(Subject(person="3ps", reflex='se', text="ela"))
	session.add(Subject(person="3ps", reflex='se', text="você"))
	session.add(Subject(person="3ps", reflex='se', text="a gente"))
	session.add(Subject(person="3pp", reflex='se', text="vocês"))
	session.add(Subject(person="3pp", reflex='se', text="eles"))
	session.add(Subject(person="3pp", reflex='se', text="elas"))
	session.add(Subject(person="3pp", reflex='se', text="John e Mary"))
	session.add(Subject(person="3pp", reflex='se', text="Lenore e Mary"))
	session.add(Subject(person="3ps", reflex='se', text="Alex"))
	session.add(Subject(person="1pp", reflex='nos', text="Pele e eu"))
	session.add(Subject(person="1pp", reflex='nos', text="eu com minha familia"))


	# Simple tenses
	session.add(Tense(id="ip", text="Indicativo Presente"))
	session.add(Tense(id="irp", text="Indicativo Pretérito Perfeito"))
	session.add(Tense(id="iri", text="Indicativo Pretérito Imperfeito"))
	session.add(Tense(id="irm", text="Indicativo Pretérito Mais-que-perfeito"))
	session.add(Tense(id="cp", text="Conditional Presente"))
	session.add(Tense(id="sp", text="Subjuntivo Presente"))
	session.add(Tense(id="st", text="Subjuntivo Pretérito Imperfeito"))
	session.add(Tense(id="sf", text="Subjuntivo Futuro"))

	# Compound tenses
	session.add(Tense(id="ipg", text="Indicativo Present Progressive", 
	    compound=True, aux_id="estar", aux_tense_id="ip"))
	session.add(Tense(id="itg", text="Indicativo Past Progressive", 
	    compound=True, aux_id="estar", aux_tense_id="iri"))
	session.add(Tense(id="ipp", text="Present Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='ip'))
	session.add(Tense(id="itr", text="Past Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='iri'))
	session.add(Tense(id="ifi", text="Future Immediate", 
	    compound=True, aux_id="ir", aux_tense_id='ip'))
	session.add(Tense(id="cpp", text="Conditional Present Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='cp'))
	session.add(Tense(id="spp", text="Subjuntivo Present Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='sp'))
	session.add(Tense(id="stp", text="Subjuntivo Past Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='st'))
	session.add(Tense(id="sfp", text="Subjuntivo Future Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='sf'))



	# Template conjugations
	session.add(Verb(id="*ar", regular=True))
	session.add(Conjugation(person="1ps", tense_id="ip", verb_id="*ar", text="STEMo"))
	session.add(Conjugation(person="3ps", tense_id="ip", verb_id="*ar", text="STEMa"))
	session.add(Conjugation(person="1pp", tense_id="ip", verb_id="*ar", text="STEMamos"))
	session.add(Conjugation(person="3pp", tense_id="ip", verb_id="*ar", text="STEMam"))

	session.add(Conjugation(person="1ps", tense_id="iri", verb_id="*ar", text="STEMava"))
	session.add(Conjugation(person="3ps", tense_id="iri", verb_id="*ar", text="STEMava"))
	session.add(Conjugation(person="1pp", tense_id="iri", verb_id="*ar", text="STEMavamos"))
	session.add(Conjugation(person="3pp", tense_id="iri", verb_id="*ar", text="STEMavam"))

	session.add(Conjugation(person="1ps", tense_id="irp", verb_id="*ar", text="STEMei"))
	session.add(Conjugation(person="3ps", tense_id="irp", verb_id="*ar", text="STEMou"))
	session.add(Conjugation(person="1pp", tense_id="irp", verb_id="*ar", text="STEMamos"))
	session.add(Conjugation(person="3pp", tense_id="irp", verb_id="*ar", text="STEMaram"))

	session.add(Conjugation(person="1ps", tense_id="cp", verb_id="*ar", text="INFia"))
	session.add(Conjugation(person="3ps", tense_id="cp", verb_id="*ar", text="INFia"))
	session.add(Conjugation(person="1pp", tense_id="cp", verb_id="*ar", text="INFiamos"))
	session.add(Conjugation(person="3pp", tense_id="cp", verb_id="*ar", text="INFiam"))

	session.add(Conjugation(person="1ps", tense_id="sp", verb_id="*ar", text="STEMe"))
	session.add(Conjugation(person="3ps", tense_id="sp", verb_id="*ar", text="STEMe"))
	session.add(Conjugation(person="1pp", tense_id="sp", verb_id="*ar", text="STEMemos"))
	session.add(Conjugation(person="3pp", tense_id="sp", verb_id="*ar", text="STEMem"))

	session.add(Conjugation(person="1ps", tense_id="st", verb_id="*ar", text="STEMasse"))
	session.add(Conjugation(person="3ps", tense_id="st", verb_id="*ar", text="STEMasse"))
	session.add(Conjugation(person="1pp", tense_id="st", verb_id="*ar", text="STEMássemos"))
	session.add(Conjugation(person="3pp", tense_id="st", verb_id="*ar", text="STEMassem"))

	session.add(Conjugation(person="1ps", tense_id="sf", verb_id="*ar", text="INF"))
	session.add(Conjugation(person="3ps", tense_id="sf", verb_id="*ar", text="INF"))
	session.add(Conjugation(person="1pp", tense_id="sf", verb_id="*ar", text="INFmos"))
	session.add(Conjugation(person="3pp", tense_id="sf", verb_id="*ar", text="INFem"))


	dar=Verb(id="*er", regular=True)
	session.add(dar)
	session.add(Conjugation(person="1ps", tense_id="ip", verb_id="*er", text="STEMo"))
	session.add(Conjugation(person="3ps", tense_id="ip", verb_id="*er", text="STEMe"))
	session.add(Conjugation(person="1pp", tense_id="ip", verb_id="*er", text="STEMemos"))
	session.add(Conjugation(person="3pp", tense_id="ip", verb_id="*er", text="STEMem"))

	session.add(Conjugation(person="1ps", tense_id="iri", verb_id="*er", text="STEMia"))
	session.add(Conjugation(person="3ps", tense_id="iri", verb_id="*er", text="STEMia"))
	session.add(Conjugation(person="1pp", tense_id="iri", verb_id="*er", text="STEMiamos"))
	session.add(Conjugation(person="3pp", tense_id="iri", verb_id="*er", text="STEMiam"))

	session.add(Conjugation(person="1ps", tense_id="irp", verb_id="*er", text="STEMi"))
	session.add(Conjugation(person="3ps", tense_id="irp", verb_id="*er", text="STEMeu"))
	session.add(Conjugation(person="1pp", tense_id="irp", verb_id="*er", text="STEMemos"))
	session.add(Conjugation(person="3pp", tense_id="irp", verb_id="*er", text="STEMeram"))

	session.add(Conjugation(person="1ps", tense_id="cp", verb_id="*er", text="INFia"))
	session.add(Conjugation(person="3ps", tense_id="cp", verb_id="*er", text="INFia"))
	session.add(Conjugation(person="1pp", tense_id="cp", verb_id="*er", text="INFiamos"))
	session.add(Conjugation(person="3pp", tense_id="cp", verb_id="*er", text="INFiam"))

	session.add(Conjugation(person="1ps", tense_id="sp", verb_id="*er", text="STEMa"))
	session.add(Conjugation(person="3ps", tense_id="sp", verb_id="*er", text="STEMa"))
	session.add(Conjugation(person="1pp", tense_id="sp", verb_id="*er", text="STEMamos"))
	session.add(Conjugation(person="3pp", tense_id="sp", verb_id="*er", text="STEMam"))

	session.add(Conjugation(person="1ps", tense_id="st", verb_id="*er", text="STEMesse"))
	session.add(Conjugation(person="3ps", tense_id="st", verb_id="*er", text="STEMesse"))
	session.add(Conjugation(person="1pp", tense_id="st", verb_id="*er", text="STEMêssemos"))
	session.add(Conjugation(person="3pp", tense_id="st", verb_id="*er", text="STEMessem"))

	session.add(Conjugation(person="1ps", tense_id="sf", verb_id="*er", text="INF"))
	session.add(Conjugation(person="3ps", tense_id="sf", verb_id="*er", text="INF"))
	session.add(Conjugation(person="1pp", tense_id="sf", verb_id="*er", text="INFmos"))
	session.add(Conjugation(person="3pp", tense_id="sf", verb_id="*er", text="INFem"))


	dar=Verb(id="*ir", regular=True)
	session.add(dar)
	session.add(Conjugation(person="1ps", tense_id="ip", verb_id="*ir", text="STEMo"))
	session.add(Conjugation(person="3ps", tense_id="ip", verb_id="*ir", text="STEMe"))
	session.add(Conjugation(person="1pp", tense_id="ip", verb_id="*ir", text="STEMimos"))
	session.add(Conjugation(person="3pp", tense_id="ip", verb_id="*ir", text="STEMem"))

	session.add(Conjugation(person="1ps", tense_id="iri", verb_id="*ir", text="STEMia"))
	session.add(Conjugation(person="3ps", tense_id="iri", verb_id="*ir", text="STEMia"))
	session.add(Conjugation(person="1pp", tense_id="iri", verb_id="*ir", text="STEMiamos"))
	session.add(Conjugation(person="3pp", tense_id="iri", verb_id="*ir", text="STEMiam"))

	session.add(Conjugation(person="1ps", tense_id="irp", verb_id="*ir", text="STEMi"))
	session.add(Conjugation(person="3ps", tense_id="irp", verb_id="*ir", text="STEMiu"))
	session.add(Conjugation(person="1pp", tense_id="irp", verb_id="*ir", text="STEMimos"))
	session.add(Conjugation(person="3pp", tense_id="irp", verb_id="*ir", text="STEMiram"))

	session.add(Conjugation(person="1ps", tense_id="cp", verb_id="*ir", text="INFia"))
	session.add(Conjugation(person="3ps", tense_id="cp", verb_id="*ir", text="INFia"))
	session.add(Conjugation(person="1pp", tense_id="cp", verb_id="*ir", text="INFiamos"))
	session.add(Conjugation(person="3pp", tense_id="cp", verb_id="*ir", text="INFiam"))

	session.add(Conjugation(person="1ps", tense_id="sp", verb_id="*ir", text="STEMa"))
	session.add(Conjugation(person="3ps", tense_id="sp", verb_id="*ir", text="STEMa"))
	session.add(Conjugation(person="1pp", tense_id="sp", verb_id="*ir", text="STEMamos"))
	session.add(Conjugation(person="3pp", tense_id="sp", verb_id="*ir", text="STEMam"))

	session.add(Conjugation(person="1ps", tense_id="st", verb_id="*ir", text="STEMisse"))
	session.add(Conjugation(person="3ps", tense_id="st", verb_id="*ir", text="STEMisse"))
	session.add(Conjugation(person="1pp", tense_id="st", verb_id="*ir", text="STEMíssemos"))
	session.add(Conjugation(person="3pp", tense_id="st", verb_id="*ir", text="STEMissem"))

	session.add(Conjugation(person="1ps", tense_id="sf", verb_id="*ir", text="INF"))
	session.add(Conjugation(person="3ps", tense_id="sf", verb_id="*ir", text="INF"))
	session.add(Conjugation(person="1pp", tense_id="sf", verb_id="*ir", text="INFmos"))
	session.add(Conjugation(person="3pp", tense_id="sf", verb_id="*ir", text="INFem"))


	with open("verbs.txt","r") as file:
		for verb in file.readlines():
			verb=verb.strip()
			print("Loading ",verb)
			load_verb(verb)

def load_rules():
	for stat in session.query(Statistic).all():
		session.delete(stat)
	for rule in session.query(Rule).all():
		session.delete(rule)
	for sentence in session.query(Sentence).all():
		session.delete(sentence)
	session.commit()

	with open("rules.txt","r") as file:
		for line in file.readlines():
			[kid,tlist,text]=line.strip().split("\t")
			session.add(Rule(tense_list=tlist,text=text))

	with open("sentences.txt","r") as file:
		for line in file.readlines():
			[kid,rid,text,subj,verb]=line.strip().split("\t")
			session.add(Sentence(rule_id=rid, text=text, 
						subj_template=subj, verb_template=verb))

	session.commit()

from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--rules-only","-r", action="store_true", help="Only load sentence templates")
	args=parser.parse_args()

	if args.rules_only:
		load_rules()
	else:
		load_db()
		load_rules()

