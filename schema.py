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

#
# The classes represent tables, and they contain members for the columns
# and constraints of the table.  These are instances of classes that are available 
# in the main sqlalchemy module
from sqlalchemy import Index, Column, Boolean, Integer, String, Unicode, DateTime, ForeignKey, func
import string

class Verb(Base):
	__tablename__ = "verbs"

	id = Column(String, primary_key=True)
	regular = Column(Boolean, default=False)
	past_part = Column(String)
	gerund = Column(String)
	ipa = Column(String)

	def __init__(self, **kw):
		Base.__init__(self,**kw)
		if not kw.get('past_part'):
			self.past_part = kw.get('id')[0:-1]+"do"
		if self.past_part[-2:-2]=='e':
			self.past_part[-2:-2]='i'
		if not kw.get('gerund'):
			self.gerund = kw.get('id')[0:-1]+"ndo"

  
	def conjugate(self, tense, subject):
		match=[x.text for x in self.conjugations if x.tense==tense and x.person==subject.person]
		if not match:
			if not tense.compound:
				defcon=self.id[-2:]
				tverb=Verb._template.get(defcon)
				match=tverb.conjugate(tense, subject)
				match=match.replace("STEM",self.id[0:-2])         
				match=match.replace("INF",self.id)         
			else:
				match=tense.aux.conjugate(tense.aux_tense, subject)
				if tense.aux_id=="estar":
				    match=match+" "+self.gerund
				elif tense.aux_id=="ir":
				    match=match+" "+self.id
				else:
				    match=match+" "+self.past_part
		else:
			match=match[0]
		return match


	def __repr__(self):
		return f"Verb({self.id!r}={self.regular!r}, {self.past_part!r}, {self.gerund!r})" 

class Tense(Base):
	__tablename__ = "tenses"
	id = Column(String, primary_key=True)
	text = Column(String)
	compound = Column(Boolean, default=False)
	aux_id = Column(String, ForeignKey("verbs.id"), nullable=True)
	aux_tense_id = Column(String, ForeignKey("tenses.id"), nullable=True)

	def __repr__(self):
		return f"Tense({self.id!r},comp={self.compound!r},aux={self.aux!r}={self.text!r})" 

class Subject(Base):
	__tablename__ = "subjects"
	id = Column(Integer, primary_key=True)
	person = Column(String, index=True)
	reflex = Column(String)
	text = Column(String)

	Index("myindex", person)

	def __repr__(self):
		return f"Subject({self.person!r}={self.text!r})" 

class Conjugation(Base):
	__tablename__ = "conjugations"
	id = Column(Integer, primary_key=True)
	person = Column(String,ForeignKey("subjects.person"))
	tense_id = Column(String, ForeignKey("tenses.id"))
	verb_id = Column(String, ForeignKey("verbs.id"))
	text = Column(String)
	def __repr__(self):
		return f"Conjugation({self.verb_id!r},{self.tense_id!r},{self.person!r}={self.text!r})" 

class Category(Base):
	__tablename__ = "categories"
	id = Column(Integer, primary_key=True)
	verb_id = Column(String, ForeignKey("verbs.id"))
	text = Column(String)
	def __repr__(self):
		return f"Category({self.verb_id!r},{self.text!r})" 

class Definition(Base):
	__tablename__ = "definitions"
	id = Column(Integer, primary_key=True)
	category_id = Column(Integer, ForeignKey("categories.id"))
	text = Column(String)
	example = Column(String)
	def __repr__(self):
		return f"Definition({self.category.text!r},{self.text!r})" 

class Synonym(Base):
	__tablename__ = "synonyms"
	id = Column(Integer, primary_key=True)
	verb_id = Column(String, ForeignKey("verbs.id"))
	related_id = Column(String)
	contrary = Column(Boolean)
	def __repr__(self):
		return f"Synonym({self.verb_id!r},{self.related_id!r},{contrary!r})" 

from sqlalchemy.orm import relationship

Synonym.verb = relationship("Verb", back_populates="synonyms")
Verb.synonyms = relationship("Synonym", back_populates="verb")

Category.verb = relationship("Verb", back_populates="categories")
Verb.categories = relationship("Category", back_populates="verb")

Category.definitions = relationship("Definition", back_populates="category")
Definition.category = relationship("Category", back_populates="definitions")

Conjugation.verb = relationship("Verb", back_populates="conjugations")
Verb.conjugations = relationship("Conjugation", back_populates="verb")

Conjugation.tense = relationship("Tense")
Tense.aux = relationship("Verb")
Tense.aux_tense = relationship("Tense",remote_side=Tense.id)


class State(Base):
	__tablename__ = "states"
	id = Column(String, primary_key=True)

class Statistic(Base):
	__tablename__ = "statistics"
	id = Column(Integer, primary_key=True)
	person = Column(String)
	sentence_id = Column(String, ForeignKey("sentences.id"), index=True)
	verb_id = Column(String, ForeignKey("verbs.id"))
	tense_id = Column(String, ForeignKey("tenses.id"))
	tested = Column(DateTime(timezone=True),server_default=func.now())
	right = Column(Boolean)
	answer = Column(String)
	correct = Column(String)

class Rule(Base):
	__tablename__ = "rules"
	id = Column(Integer, primary_key=True)
	tense_list = Column(String)
	text = Column(String)

class Sentence(Base):
	__tablename__ = "sentences"
	id = Column(Integer, primary_key=True)
	rule_id = Column(Integer, ForeignKey("rules.id"),index=True)
	text = Column(String)
	subj_template = Column(String)
	verb_template = Column(String)

Sentence.rule = relationship(Rule, back_populates="sentences")
Rule.sentences = relationship(Sentence, back_populates="rule")
Sentence.stats = relationship(Statistic, back_populates="sentence")
Statistic.sentence = relationship(Sentence, back_populates="stats")

    
# The declarative base could be bypassed by creating an external metadata object
# and passing it to a Table constructor
# from sqlalchemy import Table, MetaData
# meta=MetaData()
# name=Table('name2', meta, 
#        Column('id', Integer, primary_key=True), 
#        Column('first', String),
#        Column('last', String))

#
# So far, the backend database has been abstract, but in reality it will need
# to be a specific server (PostgreSQL, SQLite, MySQL, etc).  The adapter
# for a specific sort of DB backend is an engine, which is created with 
# create_engine and a database URL

def init(session):
	# Configure aux verbs and regular conjugation templates
	Verb._estar = session.query(Verb).filter(Verb.id=="estar").first()
	Verb._ter = session.query(Verb).filter(Verb.id=="ter").first()
	Verb._ir = session.query(Verb).filter(Verb.id=="ir").first()
	Verb._template = {
	  'ar': session.query(Verb).filter(Verb.id=="*ar").first(),
	  'er': session.query(Verb).filter(Verb.id=="*er").first(),
	  'ir': session.query(Verb).filter(Verb.id=="*ir").first()}


if __name__ == "__main__":
	from argparse import ArgumentParser as ap
	parser=ap()
	parser.add_argument("--list","-l", action="store_true", help="List Database")
	args=parser.parse_args()



