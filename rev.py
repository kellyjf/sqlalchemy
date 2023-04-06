#! /usr/bin/python3
import sqlite3
from difflib import SequenceMatcher

def simscore(x,y):
	return SequenceMatcher(None, x,y ).ratio()

def simscore2(x,y):
	lx=len(x)
	ly=len(y)
	if lx<ly:
		(x,y)=(y,x)
	cnt=0;
	for s in range(0,len(x)-len(y)+1):
		for i in range(0,len(y)):
			if x[i+s]==y[i]:
				cnt=cnt+1
	print(cnt, len(y), "%f"%(cnt/len(y)))

		
if __name__ == "__main__":
	from argparse import ArgumentParser as ap
	parser=ap()
	parser.add_argument("--analyze","-a", action="store_true", help="Analyze")
	parser.add_argument("--load","-l", action="store_true", help="Load Database")
	args=parser.parse_args()

	con=sqlite3.connect("vocab.sqlite")
	con.create_function("strrev", 1, lambda x: x[::-1])
	con.create_function("similar", 2, simscore)
	cur=con.cursor()

	if args.load:
		cur.execute("select a.entry, b.entry, similar(a.entry,b.entry) from words a, words b where a.entry > b.entry order by 3")
	else:
		cur.execute("select a.pronounce, b.pronounce, similar(a.pronounce,b.pronounce), a.entry,b.entry from words a, words b where a.pronounce > b.pronounce order by 3")
	
	for res in cur.fetchall():
		if not (res[0] in res[1] or res[1] in res[0]):
			print("\t".join([str(x) for x in res[0:]]))

