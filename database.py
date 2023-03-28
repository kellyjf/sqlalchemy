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
    regular = Column(Boolean)
    past_part = Column(String)
    gerund = Column(String)
    def __init__(self, **kw):
      if not kw.get('past_part'):
        self.past_part = kw.get('id')[0:-1]+"do"
        if self.past_part[-2:-2]=='e':
          self.past_part[-2:-2]='i'
      if not kw.get('gerund'):
        self.gerund = kw.get('id')[0:-1]+"ndo"
      Base.__init__(self,**kw)

  
    def conjugate(self, tense, subject):
        match=[x.text for x in self.conjugations if x.tense==tense and x.person==subject.person]
        if not match:
            if not tense.compound:
                defcon=self.id[-2:]
                tverb=Verb._template.get(defcon)
                #match=[x.text for x in tverb.conjugations if x.tense==tense and x.person==subject.person][0]
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
    name = Column(String)
    compound = Column(Boolean, default=False)
    aux_id = Column(String, ForeignKey("verbs.id"), nullable=True)
    aux_tense_id = Column(String, ForeignKey("tenses.id"), nullable=True)


    def __repr__(self):
        return f"Tense({self.id!r},comp={self.compound!r},aux={self.aux!r}={self.name!r})" 

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
Conjugation.tense = relationship("Tense")
Verb.conjugations = relationship("Conjugation", back_populates="verb")
Tense.aux = relationship("Verb")
Tense.aux_tense = relationship("Tense",remote_side=Tense.id)


class Clause(Base):
    __tablename__ = "clauses"
    id = Column(Integer, primary_key=True)
    sentence_id = Column(Integer, ForeignKey("sentences.id"))

class Sentence(Base):
    __tablename__ = "sentences"
    id = Column(Integer, primary_key=True)
    clauses = relationship(Clause, back_populates="sentence")
Clause.sentence = relationship(Sentence, back_populates="clauses")
    
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


    session.add(Subject(person="1ps", text="eu"))
    session.add(Subject(person="1pp", text="nós"))
    session.add(Subject(person="3ps", text="você"))
    session.add(Subject(person="3pp", text="vocês"))

    # Simple tenses
    session.add(Tense(id="ip", name="Indicative Present"))
    session.add(Tense(id="irp", name="Indicative Preterit Perfect"))
    session.add(Tense(id="iri", name="Indicative Preterit Imperfect"))
    session.add(Tense(id="cp", name="Conditional Present"))


    # Aux verbs for compound tenses
    estar=Verb(id="estar", regular=False)
    session.add(estar)
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="estar", text="estou"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="estar", text="está"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="estar", text="estamos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="estar", text="estão"))

    session.add(Conjugation(person="1ps", tense_id="iri", verb_id="estar", text="estava"))
    session.add(Conjugation(person="3ps", tense_id="iri", verb_id="estar", text="estava"))
    session.add(Conjugation(person="1pp", tense_id="iri", verb_id="estar", text="estávamos"))
    session.add(Conjugation(person="3pp", tense_id="iri", verb_id="estar", text="estavam"))

    session.add(Conjugation(person="1ps", tense_id="irp", verb_id="estar", text="estive"))
    session.add(Conjugation(person="3ps", tense_id="irp", verb_id="estar", text="esteve"))
    session.add(Conjugation(person="1pp", tense_id="irp", verb_id="estar", text="estivemos"))
    session.add(Conjugation(person="3pp", tense_id="irp", verb_id="estar", text="estiveram"))

    session.add(Conjugation(person="part", tense_id="ip", verb_id="estar", text="estando"))
    session.add(Conjugation(person="part", tense_id="irp", verb_id="estar", text="estado"))


    session.add(Verb(id="ter", regular=False))
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="ter", text="tenho"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="ter", text="tem"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="ter", text="temos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="ter", text="têm"))

    session.add(Conjugation(person="1ps", tense_id="iri", verb_id="ter", text="tinha"))
    session.add(Conjugation(person="3ps", tense_id="iri", verb_id="ter", text="tinha"))
    session.add(Conjugation(person="1pp", tense_id="iri", verb_id="ter", text="tinhamos"))
    session.add(Conjugation(person="3pp", tense_id="iri", verb_id="ter", text="tinham"))

    session.add(Conjugation(person="1ps", tense_id="irp", verb_id="ter", text="tive"))
    session.add(Conjugation(person="3ps", tense_id="irp", verb_id="ter", text="teve"))
    session.add(Conjugation(person="1pp", tense_id="irp", verb_id="ter", text="tivemos"))
    session.add(Conjugation(person="3pp", tense_id="irp", verb_id="ter", text="tiveram"))


    session.add(Verb(id="ir", regular=False))
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="ir", text="vou"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="ir", text="vai"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="ir", text="vamos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="ir", text="vão"))

    session.add(Conjugation(person="1ps", tense_id="iri", verb_id="ir", text="ia"))
    session.add(Conjugation(person="3ps", tense_id="iri", verb_id="ir", text="ia"))
    session.add(Conjugation(person="1pp", tense_id="iri", verb_id="ir", text="iamos"))
    session.add(Conjugation(person="3pp", tense_id="iri", verb_id="ir", text="iam"))

    session.add(Conjugation(person="1ps", tense_id="irp", verb_id="ir", text="fui"))
    session.add(Conjugation(person="3ps", tense_id="irp", verb_id="ir", text="foi"))
    session.add(Conjugation(person="1pp", tense_id="irp", verb_id="ir", text="fomos"))
    session.add(Conjugation(person="3pp", tense_id="irp", verb_id="ir", text="foram"))

    dar=Verb(id="*ar", regular=True)
    session.add(dar)
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="*ar", text="STEMo"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="*ar", text="STEMa"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="*ar", text="STEMamos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="*ar", text="STEMam"))

    session.add(Conjugation(person="1ps", tense_id="iri", verb_id="*ar", text="STEMava"))
    session.add(Conjugation(person="3ps", tense_id="iri", verb_id="*ar", text="STEMava"))
    session.add(Conjugation(person="1pp", tense_id="iri", verb_id="*ar", text="STEMavamos"))
    session.add(Conjugation(person="3pp", tense_id="iri", verb_id="*ar", text="STEMavam"))

    session.add(Conjugation(person="1ps", tense_id="irp", verb_id="*ar", text="STEMei"))
    session.add(Conjugation(person="3ps", tense_id="irp", verb_id="*ar", text="STEMou"))
    session.add(Conjugation(person="1pp", tense_id="irp", verb_id="*ar", text="STEMamos"))
    session.add(Conjugation(person="3pp", tense_id="irp", verb_id="*ar", text="STEMaram"))

    session.add(Conjugation(person="1ps", tense_id="cp", verb_id="*ar", text="INFia"))
    session.add(Conjugation(person="3ps", tense_id="cp", verb_id="*ar", text="INFia"))
    session.add(Conjugation(person="1pp", tense_id="cp", verb_id="*ar", text="INFiamos"))
    session.add(Conjugation(person="3pp", tense_id="cp", verb_id="*ar", text="INFiam"))


    dar=Verb(id="*er", regular=True)
    session.add(dar)
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="*er", text="STEMo"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="*er", text="STEMe"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="*er", text="STEMemos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="*er", text="STEMem"))

    session.add(Conjugation(person="1ps", tense_id="iri", verb_id="*er", text="STEMia"))
    session.add(Conjugation(person="3ps", tense_id="iri", verb_id="*er", text="STEMia"))
    session.add(Conjugation(person="1pp", tense_id="iri", verb_id="*er", text="STEMiamos"))
    session.add(Conjugation(person="3pp", tense_id="iri", verb_id="*er", text="STEMiam"))

    session.add(Conjugation(person="1ps", tense_id="irp", verb_id="*er", text="STEMi"))
    session.add(Conjugation(person="3ps", tense_id="irp", verb_id="*er", text="STEMeu"))
    session.add(Conjugation(person="1pp", tense_id="irp", verb_id="*er", text="STEMemos"))
    session.add(Conjugation(person="3pp", tense_id="irp", verb_id="*er", text="STEMeram"))

    session.add(Conjugation(person="1ps", tense_id="cp", verb_id="*er", text="INFia"))
    session.add(Conjugation(person="3ps", tense_id="cp", verb_id="*er", text="INFia"))
    session.add(Conjugation(person="1pp", tense_id="cp", verb_id="*er", text="INFiamos"))
    session.add(Conjugation(person="3pp", tense_id="cp", verb_id="*er", text="INFiam"))


    dar=Verb(id="*ir", regular=True)
    session.add(dar)
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="*ir", text="STEMo"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="*ir", text="STEMe"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="*ir", text="STEMimos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="*ir", text="STEMem"))

    session.add(Conjugation(person="1ps", tense_id="iri", verb_id="*ir", text="STEMia"))
    session.add(Conjugation(person="3ps", tense_id="iri", verb_id="*ir", text="STEMia"))
    session.add(Conjugation(person="1pp", tense_id="iri", verb_id="*ir", text="STEMiamos"))
    session.add(Conjugation(person="3pp", tense_id="iri", verb_id="*ir", text="STEMiam"))

    session.add(Conjugation(person="1ps", tense_id="irp", verb_id="*ir", text="STEMi"))
    session.add(Conjugation(person="3ps", tense_id="irp", verb_id="*ir", text="STEMiu"))
    session.add(Conjugation(person="1pp", tense_id="irp", verb_id="*ir", text="STEMimos"))
    session.add(Conjugation(person="3pp", tense_id="irp", verb_id="*ir", text="STEMiram"))

    session.add(Conjugation(person="1ps", tense_id="cp", verb_id="*ir", text="INFia"))
    session.add(Conjugation(person="3ps", tense_id="cp", verb_id="*ir", text="INFia"))
    session.add(Conjugation(person="1pp", tense_id="cp", verb_id="*ir", text="INFiamos"))
    session.add(Conjugation(person="3pp", tense_id="cp", verb_id="*ir", text="INFiam"))


    # Irregular verbs
    session.add(Verb(id="vir", regular=False, past_part="vindo"))
    session.add(Conjugation(person="1ps", tense_id="ip", verb_id="vir", text="venho"))
    session.add(Conjugation(person="3ps", tense_id="ip", verb_id="vir", text="vem"))
    session.add(Conjugation(person="1pp", tense_id="ip", verb_id="vir", text="vimos"))
    session.add(Conjugation(person="3pp", tense_id="ip", verb_id="vir", text="vêm"))

    session.add(Conjugation(person="1ps", tense_id="irp", verb_id="vir", text="vim"))
    session.add(Conjugation(person="3ps", tense_id="irp", verb_id="vir", text="veio"))
    session.add(Conjugation(person="1pp", tense_id="irp", verb_id="vir", text="viemos"))
    session.add(Conjugation(person="3pp", tense_id="irp", verb_id="vir", text="vieram"))

    session.add(Conjugation(person="1ps", tense_id="iri", verb_id="vir", text="vinha"))
    session.add(Conjugation(person="3ps", tense_id="iri", verb_id="vir", text="vinha"))
    session.add(Conjugation(person="1pp", tense_id="iri", verb_id="vir", text="vinhamos"))
    session.add(Conjugation(person="3pp", tense_id="iri", verb_id="vir", text="vinham"))

    session.add(Conjugation(person="part", tense_id="ip", verb_id="vir", text="vindo"))
    session.add(Conjugation(person="part", tense_id="irp", verb_id="vir", text="vindo"))

    # Compound tenses
    session.add(Tense(id="ipg", name="Indicative Present Progressive", 
            compound=True, aux_id="estar", aux_tense_id="ip"))
    session.add(Tense(id="itg", name="Indicative Past Progressive", 
            compound=True, aux_id="estar", aux_tense_id="iri"))
    session.add(Tense(id="ipp", name="Present Perfect", 
            compound=True, aux_id="ter", aux_tense_id='ip'))
    session.add(Tense(id="itr", name="Past Perfect", 
            compound=True, aux_id="ter", aux_tense_id='iri'))
    session.add(Tense(id="ifi", name="Future Immediate", 
            compound=True, aux_id="ir", aux_tense_id='ip'))
    session.add(Tense(id="cpp", name="Conditional Present Perfect", 
            compound=True, aux_id="ter", aux_tense_id='cp'))



    session.commit()


# a=session.query(Conjugation).filter(Conjugation.verb_id.in_(["estar","vir"])).filter(Conjugation.tense_id=="iri")

# For data manipulation, we can create a connection to the backend
# for direct SQL access
connect=engine.connect()

# Or we can create a session to manage transactions
from sqlalchemy.orm import Session
session=Session(engine)

def finish(session):
    Verb._estar = session.query(Verb).filter(Verb.id=="estar").first()
    Verb._ter = session.query(Verb).filter(Verb.id=="ter").first()
    Verb._ir = session.query(Verb).filter(Verb.id=="ir").first()
    Verb._template = {
          'ar': session.query(Verb).filter(Verb.id=="*ar").first(),
          'er': session.query(Verb).filter(Verb.id=="*er").first(),
          'ir': session.query(Verb).filter(Verb.id=="*ir").first()}

#finish(session)


create()
load()
finish(session)
v=Verb(id='falar')
s=session.query(Subject).all()
t=session.query(Tense).all()


from argparse import ArgumentParser as ap
if __name__ == "__main__":
  parser=ap()
  parser.add_argument("--list","-l", action="store_true", help="List Database")
  args=parser.parse_args()



