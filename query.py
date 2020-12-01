#!/usr/bin/python3

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from fuzzywuzzy import fuzz

engine = create_engine('sqlite:///test.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base(engine)
class Moa(Base):
    __tablename__ = 'moa'

    drugbank_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    pd = Column(String)
    mechanism = Column(String)

names = [row.name for row  in session.query(Moa.name)]
# Column mapping
cols = {
    'Pharmacodynamics': Moa.pd,
    'Mechanism of action': Moa.mechanism
}

          
def search(names):
    '''
    Takes user input and matches it against rows in name column

    Returns
        search - matched name in table
    '''
    while True:
        search = input('Search:').lower()
        if search == 'quit':
            break
        if search == '':
            print('Please enter a search term.')
            continue
        # Capitalise first letter
        search = search[0].upper() + search[1:]

        if search not in names:
            # Return name with highest similarity score
            similarities = {}
            for name in names:
                similarity = fuzz.token_sort_ratio(name.lower(), search.lower())
                #print(name.lower(), search.lower(), similarity)
                similarities.update({name.lower(): similarity})
            search =  max(similarities, key = similarities.get)
            print('Did you mean:', search, '?')
        search = search[0].upper() + search[1:]
        return search
    
query = search(names)

def match(key, value, query):
    '''
    
    '''
    result = session.query(value).filter(Moa.name == query).all()
    print('--' + key + '--\n' + result[0][0] + '\n')
    

for key, value in cols.items():
    match(key, value, query)


#result_mechanism = session.query(Moa.mechanism).filter(Moa.name == query).all()
#result_pd = session.query(Moa.pd).filter(Moa.name == query).all()

#print('--Mechanism of action--\n', result_mechanism[0][0], '\n')
#print('--Pharmacodynamics--\n', result_pd[0][0], '\n')

