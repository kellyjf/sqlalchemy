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
from sqlalchemy import Column, Integer, String, Unicode, DateTime, ForeignKey, func

class Name(Base):
    __tablename__ = "names"
    id = Column(Integer, primary_key=True)
    first = Column(String)
    last = Column(String)

# The declarative base could be bypassed by creating an external metadata object
# and passing it to a Table constructor
from sqlalchemy import Table, MetaData
meta=MetaData()
name=Table('name2', meta, 
       Column('id', Integer, primary_key=True), 
       Column('first', String),
       Column('last', String))

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
    meta.create_all(engine)

from sqlalchemy.orm import Session
session=Session(engine)



from sqlalchemy.orm import relationship



from argparse import ArgumentParser as ap
if __name__ == "__main__":
	parser=ap()
	parser.add_argument("--list","-l", action="store_true", help="List Database")
	args=parser.parse_args()



