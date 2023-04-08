#!/usr/bin/python3


import os.path
import re
import subprocess 


# word - lookup key onweb and file name
# infinitivo -infinitive form of the word, for text output and database keys	
def ipa(word):
	cmd = ['espeak', '-q', '-v', 'pt-BR', '--ipa', word]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	p.wait()
	ipa=p.stdout.read().strip().decode('utf-8')
	return ipa.replace("\n",", ")


from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--rules-only","-r", action="store_true", help="Only load sentence templates")
	args=parser.parse_args()

	with open("vocab.txt","r") as f:
		for num,line in enumerate(f.readlines()):
			if num<16:
				print(line,end="")
			else:
				f=line.split("\t")
				f[2]=ipa(f[1])
				print("\t".join(f),end="")


