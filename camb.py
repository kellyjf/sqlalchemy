#!/usr/bin/python3


import requests
from lxml import html
import sqlite3
from schema import Synonym,Definition,Category,Statistic, Subject, Verb, Tense, Conjugation, Sentence, Rule, State, Base, init
import os.path
import re
import subprocess 

from sqlalchemy import create_engine, not_
engine=create_engine("sqlite:///portuguese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)


# verb - lookup key onweb and file name
# infinitivo -infinitive form of the verb, for text output and database keys	
def load_ipa(verb):
	verbreg=True
	cmd = ['espeak', '-q', '-v', 'pt-BR', '--ipa', verb.id ]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	p.wait()
	verb.ipa=p.stdout.read().strip().decode('utf-8')
	session.add(verb)
	session.commit()			


from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--rules-only","-r", action="store_true", help="Only load sentence templates")
	args=parser.parse_args()
	for cat in session.query(Category).all():
		session.delete(cat)
	session.commit()
	#for verb in session.query(Verb).filter(not_(Verb.id.like('*%'))).all():
	for verb in session.query(Verb).all():
			print(f"IPA for {verb.id}")
			load_ipa(verb)


