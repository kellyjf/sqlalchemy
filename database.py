#!/usr/bin/python3


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker,relationship
from sqlalchemy import create_engine, Column, Integer, String, Unicode, DateTime, ForeignKey, func
from argparse import ArgumentParser as ap

Base=declarative_base()
engine=create_engine("sqlite:///DATABASE.sqlite")
Session=sessionmaker(bind=engine)

# How to do multiple column foreign keys
#__table_args__ = (ForeignKeyConstraint([marktime,pid],[Process.marktime,Process.pid]),{})

class Root(Base):
	__tablename__ = "roots"

	id = Column(Integer, primary_key=True)
	root = Column(Unicode)
	importance = Column(Integer)
	created = Column(DateTime)
	usages = relationship("Usage",back_populates='root',cascade="all, delete-orphan")
	encounters = relationship("Encounter",back_populates='root',cascade="all, delete-orphan")

class Encounter(Base):
	__tablename__ = "encounters"

	id = Column(Integer, primary_key=True)
	root_id = Column(Integer, ForeignKey('roots.id'))
	root = relationship("Root",back_populates='encounters')
	media_id = Column(Integer, ForeignKey('media.id'))
	media = relationship("Media",back_populates='encounters')
	skill = Column(Integer)
	encounter_time = Column(DateTime)
	notes = Column(String)

class Media(Base):
	__tablename__ = "media"

	id = Column(Integer, primary_key=True)
	encounters = relationship("Encounter",back_populates='media',cascade="all, delete-orphan")
	name = Column(String)
	notes = Column(String)
	url = Column(String)
	created = Column(DateTime)



def create():
	Base.metadata.create_all(engine)

if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--list","-l", action="store_true", help="List Database")
	args=parser.parse_args()

	create()


