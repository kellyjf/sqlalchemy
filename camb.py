#!/usr/bin/python3


import os.path
import re
import subprocess 


#
# SQLAlchemy creates an object heirarchy that adapts python code classes
# to DB tables.  By subclassing all these adapter objects from a declariative
# base table, code can traverse the object tree to detect the structure of 
# the object heirarchy, and create schema DDL so that the database can be created
# from the derived SQL
#
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()

#
# The classes represent tables, and they contain members for the columns
# and constraints of the table.  These are instances of classes that are available 
# in the main sqlalchemy module
from sqlalchemy import Index, Column, Boolean, Integer, String, Unicode, DateTime, ForeignKey, func
import string



class Word(Base):
	__tablename__ = "words"

	id = Column(String, primary_key=True)
	gendered = Column(String)
	pron = Column(String)
	define = Column(String)
	example = Column(String)
	picture = Column(String)
	ipa = Column(String)


# word - lookup key onweb and file name
# infinitivo -infinitive form of the word, for text output and database keys	
def load_ipa(word):
	cmd = ['espeak', '-q', '-v', 'pt-BR', '--ipa', word.gendered]
	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	p.wait()
	word.ipa=p.stdout.read().strip().decode('utf-8')


from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--rules-only","-r", action="store_true", help="Only load sentence templates")
	args=parser.parse_args()

	from sqlalchemy import create_engine, not_
	from sqlalchemy.orm import Session

	engine=create_engine("sqlite:///vocab.sqlite")
	Base.metadata.create_all(engine)
	session=Session(engine)

	for word in session.query(Word).all():
		session.delete(word)
	session.commit()

	with open("vocab.txt","r") as f:
		for line in f.readlines()[16:]:
			[vid,gendered,pron,define,example,picture]=line.strip().split("\t")[0:6]
			word=session.query(Word).filter(Word.id==vid).first()
			if not word:
				word=Word(id=vid,gendered=gendered,pron=pron,define=define,example=example,picture=picture)
			else:
				print("DUP",word,line)

			load_ipa(word)
			session.add(word)
			session.commit()


