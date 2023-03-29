#!/usr/bin/python3


from schema import Subject, Verb, Tense, Conjugation, Sentence, Clause, Meaning, Case, Base, init as schinit
import os.path

from sqlalchemy import create_engine
engine=create_engine("sqlite:///portugese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)

def load_meanings():
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

def testme():
	ss=session.query(Subject).all()
	ms=session.query(Meaning).filter(Meaning.tense_id=="iri").all()
	for m in ms:
		print(m.tense.name, m.order, m.text)
		for c in m.clauses:
			print(c.text)
			for k in c.cases:
				for s in ss:
					print(s.text,k.verb.conjugate(m.tense, s))


if __name__ == "__main__":
	schinit(session)
	load_meanings()

