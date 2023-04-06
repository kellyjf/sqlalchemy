#!/usr/bin/python3

#
# SQLAlchemy creates an object heirarchy that adapts python code classes
# to DB tables.  By subclassing all these adapter objects from a declariative
# base table, code can traverse the object tree to detect the structure of 
# the object heirarchy, and create schema DDL so that the database can be created
# from the derived SQL
#
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()

from sqlalchemy import create_engine
engine=create_engine("sqlite:///vocab.sqlite")
from sqlalchemy.orm import Session
session=Session(engine)

#
# The classes represent tables, and they contain members for the columns
# and constraints of the table.  These are instances of classes that are available 
# in the main sqlalchemy module
from sqlalchemy import Index, Column, Boolean, Integer, String, Unicode, DateTime, ForeignKey, func
import string

class Word(Base):
	__tablename__ = "words"

	id = Column(Integer, primary_key=True)
	entry = Column(String)
	gendered = Column(String)
	pronounce = Column(String)
	define = Column(String)
	example = Column(String)


if __name__ == "__main__":
	from argparse import ArgumentParser as ap
	parser=ap()
	parser.add_argument("--analyze","-a", action="store_true", help="Analyze")
	parser.add_argument("--load","-l", action="store_true", help="Load Database")
	args=parser.parse_args()


	if args.load:
		Base.metadata.create_all(engine)
		with open("portvocab.txt","r") as file:
			for line in file.readlines():
				[entry,gendered,pronounce,define,example]=line.split("\t")[:5]
				session.add(Word(entry=entry,gendered=gendered,pronounce=pronounce,define=define,example=example))
		session.commit()

	if args.analyze:
		with engine.connect() as con:
			con.create_function("strrev", 1, lambda x: x[::-1])
			cur=con.cursor()
			cur.execute("select strrev(entry),entry,pronounce from words order by 1")
			for res in cur.fetchall():
				print(res[0:])

