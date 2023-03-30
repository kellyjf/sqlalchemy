#!/usr/bin/python3


from schema import Rule, Subject, Verb, Tense, Conjugation, Statistic, Sentence, Clause, Meaning, Case, Base, init as schinit
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

def make():
	pass

for s in session.query(Sentence).all():
	session.delete(s)
for s in session.query(Rule).all():
	session.delete(s)
for s in session.query(Statistic).all():
	session.delete(s)
session.commit()

r=Rule(text="Hypothetical Regrets")
session.add(r)
#s=Sentence(text="S1 V1, S2 V2", subj_template="eu você ; você eu ; ele% $1",verb_template="cp:comprar,dormir ip:$1", rule=r)
s=Sentence(text="dois mais dois V1 quatro", subj_template="eles",verb_template="ip:ser", rule=r)
session.add(s)
session.commit()

s=session.query(Sentence).first()

import itertools

stemp = s.subj_template
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

vtemp = s.verb_template
vres=[]
vq=session.query(Verb)
for vg in vtemp.strip().split(";"):
	vgr=[]
	for vpc in vg.strip().split(" "):
		[vt,vp]=vpc.strip().split(":")
		vpr=[]
		for vv in vp.strip().split(","):
			if vv[0]=='$':
				vpr.extend([(vt,vv)])
			else:
				vpr.extend([(vt,x) for x in vq.filter(Verb.id.like(vv)).all()])
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
	output=s.text
	for ndx, subj in enumerate(slist):
		odx=ndx+1
		(vt,verb)=vlist[ndx]
		output=output.replace(f"S{odx}",subj.text)
		output=output.replace(f"V{odx}",verb.conjugate(session.query(Tense).filter(Tense.id==vt).first(),subj))
	print(output)
		

from argparse import ArgumentParser as ap
if __name__ == "__dmain__":
	parser=ap()
	parser.add_argument("--tense","-t", nargs="*", action="store", help="Tenses")
	parser.add_argument("--verb","-v", nargs="*", action="store", help="Tenses")
	args=parser.parse_args()

	schinit(session)
	testme(args.tense, args.verb)

