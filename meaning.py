#!/usr/bin/python3


from schema import Subject, Verb, Tense, Conjugation, Sentence, Clause, Meaning, Case, Base
import os.path

from sqlalchemy import create_engine
engine=create_engine("sqlite:///portugese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)

def load():
	for c in session.query(Case).all():
		session.delete(c)
	for c in session.query(Meaning).all():
		session.delete(c)
	for c in session.query(Clause).all():
		session.delete(c)
	for c in session.query(Sentence).all():
		session.delete(c)
	session.commit()

	with open("meaning.txt", "r") as file:
		for line in file.readlines():
			[tense_id, order, desc, text, verblist]=line[:-1].split("\t")
			m=Meaning(tense_id=tense_id, order=order, text=desc)
			session.add(m)
			c=Clause(meaning=m, verb_template=verblist, text=text)
			session.add(c)
			vlist=verblist.split(" ")
			q=session.query(Verb)
			for verb in verblist.split(" "):
				for v in q.filter(Verb.id==verb).all():
					session.add(Case(clause=c,verb=v))
			session.commit()
			print(line)


load()

