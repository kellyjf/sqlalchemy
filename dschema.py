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

class Word(Base):
	__tablename__ = "words"

	id = Column(String, primary_key=True)
	plural = Column(String)
	ipa = Column(String)


class Category(Base):
	__tablename__ = "categories"
	id = Column(Integer, primary_key=True)
	word_id = Column(String, ForeignKey("words.id"))
	text = Column(String)
	def __repr__(self):
		return f"Category({self.word_id!r},{self.text!r})" 

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
	word_id = Column(String, ForeignKey("words.id"))
	related_id = Column(String)
	contrary = Column(Boolean)
	def __repr__(self):
		return f"Synonym({self.word_id!r},{self.related_id!r},{contrary!r})" 

class Example(Base):
	__tablename__ = "examples"
	id = Column(Integer, primary_key=True)
	word_id = Column(String, ForeignKey("words.id"))
	text = Column(String)
	source = Column(String)
	phrase = Column(Boolean)

	def __repr__(self):
		return f"Example({self.word_id!r},{self.text!r})" 

from sqlalchemy.orm import relationship

Synonym.verb = relationship("Word", back_populates="synonyms")
Word.synonyms = relationship("Synonym", back_populates="verb")

Category.verb = relationship("Word", back_populates="categories")
Word.categories = relationship("Category", back_populates="verb")

Category.definitions = relationship("Definition", back_populates="category")
Definition.category = relationship("Category", back_populates="definitions")

Example.word = relationship("Word", back_populates="examples")
Word.examples = relationship("Example", back_populates="word")


if __name__ == "__main__":
	from argparse import ArgumentParser as ap
	parser=ap()
	parser.add_argument("--list","-l", action="store_true", help="List Database")
	args=parser.parse_args()



