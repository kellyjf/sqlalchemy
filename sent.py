#!/usr/bin/python3


from schema import Rule, Subject, Verb, Tense, Conjugation, Statistic, Sentence, Clause, Meaning, Case, Base, init as schinit
import os.path
import random
import itertools

from sqlalchemy import create_engine
engine=create_engine("sqlite:///portugese.sqlite")
Base.metadata.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)

tensemap={ x.id: x for x in session.query(Tense).all()}

def quizline(sentence,tenseids,verbs):
	print(sentence,tenseids,verbs)
	stemp = sentence.subj_template
	sres=[]
	sq=session.query(Subject)
	for sg in stemp.strip().split(";"):
		sgr=[]
		for sp in sg.strip().split(" "):
			spr=[]
			for sv in sp.strip().split(","):
				if sv[0]=='$':
					spr.extend([sv])
				else:
					spr.extend(sq.filter(Subject.text.like(sv)).all())
			sgr.append(spr)
		sgt=list(itertools.product(*sgr))
		sres.extend(sgt)

	vtemp = sentence.verb_template
	vres=[]
	vq=session.query(Verb)
	for vg in vtemp.strip().split(";"):
		vgr=[]
		for vpc in vg.strip().split(" "):
			[vt,vp]=vpc.strip().split(":")
			vpr=[]
			for vv in vp.strip().split(","):
				vtt=tensemap.get(vt)
				if vv[0]=='$':
					vpr.extend([(vtt,vv)])
				else:
					vpr.extend([(vtt,x) for x in vq.filter(Verb.id.like(vv)).all()])
			vgr.append(vpr)
		vgt=list(itertools.product(*vgr))
		vres.extend(vgt)

	cases=list(itertools.product(sres,vres))
	random.shuffle(cases)
	for slist,vlist in cases:
		#print(slist,vlist)
		slist=list(slist)
		for ndx,si in enumerate(slist):
			if type(si)==str:
				ref=int(si[1:])-1
				slist[ndx]=slist[ref]
		vlist=list(vlist)
		for vspec in vlist:
			(vt,verb)=vspec
			if type(verb)==str:
				ref=int(verb[1:])-1
				vlist[ndx]=(vt,vlist[ref][1])

		schinit(session)
		question=sentence.text
		correct=sentence.text
		qlist=[]
		for ndx, subj in enumerate(slist):
			odx=ndx+1
			(vt,verb)=vlist[ndx]
			correct=correct.replace(f"S{odx}",subj.text)
			correct=correct.replace(f"V{odx}",verb.conjugate(vt,subj))
			question=question.replace(f"S{odx}",subj.text)
			if verb.id not in verbs:
				question=question.replace(f"V{odx}",verb.conjugate(vt,subj))
				
			else:
				question=question.replace(f"V{odx}",f"[__({verb.id})___]")
				qlist.append((subj,vt,verb,verb.id,verb.conjugate(vt,subj)))
		print(question)
		for (subject, tense, verb, prompt, good) in qlist:
			print(prompt, end=": ")
			ans=input()
			if ans==good:
				print("Correct!")
			else:
				print(f"Wrong, its {good}")
			stat=Statistic(sentence_id=sentence.id,verb_id=verb.id,tense_id=tense.id,
				  person=subject.person, 
				  right=(ans==good), answer=ans, correct=good)
			session.add(stat)
			session.commit()

		print(correct)
			
def quiz(tenseids,verbs):
	for sentence in session.query(Sentence).all():
		quizline(sentence,tenseids,verbs)

from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--tense","-t", nargs="*", action="store", help="Tenses")
	parser.add_argument("--verb","-v", nargs="*", action="store", help="Tenses")
	args=parser.parse_args()

	schinit(session)
	quiz(args.tense, args.verb)

