#!/usr/bin/python3


from schema import Subject, Verb, Tense, Conjugation, Statistic, Sentence, Clause, Meaning, Case, Base, init as schinit
import os.path
import random

from sqlalchemy import create_engine
engine=create_engine("sqlite:///portugese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)

def testme(tense,verb):
	m=session.query(Subject,Case).join(Clause).join(Meaning)
	if tense:
		m=m.filter(Meaning.tense_id.in_(tense))
	if verb:
		m=m.filter(Case.verb_id.in_(verb))
	ms=m.all()
	random.shuffle(ms)
	for subj,case in ms:
		template=case.clause.text
		print()
		print(f"{case.clause.meaning.text}  ({case.clause.meaning.tense.text})")
		print(template.replace("SUBJ",subj.text).replace("VERB",f"[__({case.verb.id})__]"))
		ans=input()
		correct=case.verb.conjugate(case.clause.meaning.tense, subj)
		if ans==correct:
			right=True
			case.correct=case.correct+1
			print("CORRECT")
		else:
			right=False
			case.wrong=case.wrong+1
			print("WRONG")
			print(template.replace("SUBJ",subj.text).replace("VERB",correct))
			y=input()
		session.add(Statistic(person=subj.person,verb_id=case.verb_id,
					tense_id=case.clause.meaning.tense_id,
					right=right,correct=correct,answer=ans))
		session.add(case)
		session.commit()

from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--tense","-t", nargs="*", action="store", help="Tenses")
	parser.add_argument("--verb","-v", nargs="*", action="store", help="Tenses")
	args=parser.parse_args()

	schinit(session)
	testme(args.tense, args.verb)


