#!/usr/bin/python3


import requests
from lxml import html
import sqlite3
from schema import Subject, Verb, Tense, Conjugation, Base
import os.path

from sqlalchemy import create_engine
engine=create_engine("sqlite:///portugese.sqlite")
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
	if not infinitivo:
		infinitivo=verb
	if not os.path.exists(f"net/{verb}.txt"):
		r=requests.get(f"https://www.conjugacao.com.br/verbo-{verb}/")
		verbreg=True
		if r.status_code==200:
			with open(f"net/{verb}.txt","wb") as fd:
				fd.write(r.content)

	with open(f"net/{verb}.txt","rb") as fd:
		tree=html.fromstring(fd.read())
		parts=tree.xpath("//div[@class='info-v']")
		for part in parts:
			pparts=part.xpath(".//span[@class='f']")
			if len(pparts)>1:
				gerund=pparts[0].text
				past_part=pparts[1].text
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
						session.add(Conjugation(verb_id=infinitivo, tense_id=tkey, person=person, text=text))
		session.add(Verb(id=infinitivo, gerund=gerund, past_part=past_part))

def load_db():

	# Subjects
	session.add(Subject(person="1ps", text="eu"))
	session.add(Subject(person="1pp", text="nós"))
	session.add(Subject(person="3ps", text="você"))
	session.add(Subject(person="3pp", text="vocês"))


	# Simple tenses
	session.add(Tense(id="ip", name="Indicative Present"))
	session.add(Tense(id="irp", name="Indicative Preterit Perfect"))
	session.add(Tense(id="iri", name="Indicative Preterit Imperfect"))
	session.add(Tense(id="cp", name="Conditional Present"))
	session.add(Tense(id="sp", name="Subjunctive Present"))
	session.add(Tense(id="st", name="Subjunctive Past"))
	session.add(Tense(id="sf", name="Subjunctive Future"))

	# Compound tenses
	session.add(Tense(id="ipg", name="Indicative Present Progressive", 
	    compound=True, aux_id="estar", aux_tense_id="ip"))
	session.add(Tense(id="itg", name="Indicative Past Progressive", 
	    compound=True, aux_id="estar", aux_tense_id="iri"))
	session.add(Tense(id="ipp", name="Present Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='ip'))
	session.add(Tense(id="itr", name="Past Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='iri'))
	session.add(Tense(id="ifi", name="Future Immediate", 
	    compound=True, aux_id="ir", aux_tense_id='ip'))
	session.add(Tense(id="cpp", name="Conditional Present Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='cp'))
	session.add(Tense(id="spp", name="Subjunctive Present Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='sp'))
	session.add(Tense(id="stp", name="Subjunctive Past Perfect", 
	    compound=True, aux_id="ter", aux_tense_id='st'))
	session.add(Tense(id="sfp", name="Subjunctive Future Perfect", 
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



	verbs= [
		'ser', 'estar', 'ter', 'ir', 'vir',
		'ver', 'ouvir', 'olhar', 'ler',
		'querer', 'dizer', 'fazer',
		'saber', 'haver', 
		'dar', 'trazer', 'pedir', 'medir', 'vestir', 'seguir',
		'aprender', 'entender', 'estudar', 'falar', 'conhecer' ]


	load_verb('por','pôr')

	for verb in verbs:
		print("Loading ",verb)

		load_verb(verb)

		session.commit()


load_db()

