#!/usr/bin/python3
"""Maps models to existing muler.db tables

Classes
------
Pharm
Name
Synonym
Product
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

engine = create_engine('sqlite:///muler.db', echo=False)

Base = declarative_base(engine)

class Pharm(Base):
    __tablename__ = 'pharm'

    drugbank_id = Column(String, primary_key=True)
    pd = Column(String)
    mech = Column(String)
    ind = Column(String)
    d_class = Column(String)

class Name(Base):
    __tablename__ = 'name'

    drugbank_id = Column(String, primary_key=True)
    name = Column(String)

class Synonym(Base):
    __tablename__ = 'synonym'

    drugbank_id = Column(String, ForeignKey(Name.drugbank_id), primary_key=True)
    synonym = Column(String)
    name = relationship('Name', backref = 'synonym')

class Product(Base):
    __tablename__ = 'product'

    drugbank_id = Column(String, ForeignKey(Name.drugbank_id), primary_key=True)
    product = Column(String)
    name = relationship('Name', backref = 'product')

if __name__ == '__main__':
    print('models.py executed.')

