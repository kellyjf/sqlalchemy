#!/usr/bin/python3


from schema import Subject, Verb, Tense, Conjugation, Sentence, Clause, Meaning, Case, Base, init as schinit
import os.path

from sqlalchemy import create_engine
engine=create_engine("sqlite:///portugese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)

def testme():
	ss=session.query(Subject).all()
	ms=session.query(Meaning).filter(Meaning.tense_id=="iri").all()
	for m in ms:
		print(m.tense.name, m.order, m.text)
		for c in m.clauses:
			template=c.text
			for k in c.cases:
				for s in ss:
					print(template.replace("SUBJ",s.text).replace("VERB",f"__({k.verb.id})__"))
					print(template.replace("SUBJ",s.text).replace("VERB",k.verb.conjugate(m.tense, s)))


if __name__ == "__main__":
	schinit(session)
	testme()

