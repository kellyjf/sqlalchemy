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

class Verb(Base):
    __tablename__ = "verbs"
    id = Column(String, primary_key=True)
    regular = Column(Boolean)
    def __repr__(self):
        return f"Verb({self.id!r}={self.regular!r})" 

class Tense(Base):
    __tablename__ = "tenses"
    id = Column(String, primary_key=True)
    name = Column(String)
    def __repr__(self):
        return f"Subject({self.id!r}={self.name!r})" 

class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    person = Column(String, index=True)
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

from sqlalchemy.orm import relationship
Conjugation.verb = relationship("Verb", back_populates="conjugations")
Verb.conjugations = relationship("Conjugation", back_populates="verb")



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
from sqlalchemy import create_engine
engine=create_engine("sqlite:///hello.sqlite")

#
# Now the database DDL can be marshalled from the metadata and sent to the engine
# to initialize the database in the backend
#
def create():
    Base.metadata.create_all(engine)
#    meta.create_all(engine)

def load():
    Base.metadata.create_all(engine)

    session.add(Tense(id="ip", name="Indicative Present"))
    session.add(Tense(id="ipp", name="Indicative Preterit Perfect"))
    session.add(Tense(id="ipi", name="Indicative Preterit Imperfect"))

    session.add(Subject(person="1ps", text="eu"))
    session.add(Subject(person="1pp", text="nós"))
    session.add(Subject(person="3ps", text="você"))
    session.add(Subject(person="3pp", text="vocês"))

    session.add(Verb(id="vir", regular=False))
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="vir", text="venho"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="vir", text="vem"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="vir", text="vimos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="vir", text="vêm"))

    session.add(Conjugation(person="1ps", tense_id="ipp", verb_id="vir", text="vim"))
    session.add(Conjugation(person="3ps", tense_id="ipp", verb_id="vir", text="veio"))
    session.add(Conjugation(person="1pp", tense_id="ipp", verb_id="vir", text="viemos"))
    session.add(Conjugation(person="3pp", tense_id="ipp", verb_id="vir", text="vieram"))

    session.add(Conjugation(person="1ps", tense_id="ipi", verb_id="vir", text="vinha"))
    session.add(Conjugation(person="3ps", tense_id="ipi", verb_id="vir", text="vinha"))
    session.add(Conjugation(person="1pp", tense_id="ipi", verb_id="vir", text="vinhamos"))
    session.add(Conjugation(person="3pp", tense_id="ipi", verb_id="vir", text="vinham"))

    session.add(Verb(id="estar", regular=False))
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="estar", text="estou"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="estar", text="está"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="estar", text="estamos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="estar", text="estão"))

    session.add(Conjugation(person="1ps", tense_id="ipi", verb_id="estar", text="estava"))
    session.add(Conjugation(person="3ps", tense_id="ipi", verb_id="estar", text="estava"))
    session.add(Conjugation(person="1pp", tense_id="ipi", verb_id="estar", text="estávamos"))
    session.add(Conjugation(person="3pp", tense_id="ipi", verb_id="estar", text="estavam"))

    session.add(Conjugation(person="1ps", tense_id="ipp", verb_id="estar", text="estive"))
    session.add(Conjugation(person="3ps", tense_id="ipp", verb_id="estar", text="esteve"))
    session.add(Conjugation(person="1pp", tense_id="ipp", verb_id="estar", text="estivemos"))
    session.add(Conjugation(person="3pp", tense_id="ipp", verb_id="estar", text="estiveram"))

    session.commit()
# a=session.query(Conjugation).filter(Conjugation.verb_id.in_(["estar","vir"])).filter(Conjugation.tense_id=="ipi")

# For data manipulation, we can create a connection to the backend
# for direct SQL access
connect=engine.connect()

# Or we can create a session to manage transactions
from sqlalchemy.orm import Session
session=Session(engine)






from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--list","-l", action="store_true", help="List Database")
	args=parser.parse_args()



