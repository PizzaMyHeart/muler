#!/usr/bin/env python3

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from fuzzywuzzy import fuzz
from muler.models import Pharm, Name, Synonym, Product
from muler.database.regex import drop_tags
import muler.config as config

def db_session():
    '''Establish a connection to the database'''
    db_url = config.db_config['local_mysql_db'] # Change this when deploying
    # Set pool_recycle to < 300 to avoid disconnection errors.
    # See https://help.pythonanywhere.com/pages/UsingSQLAlchemywithMySQL
    engine = create_engine(db_url, echo=False, pool_recycle=280, connect_args={'connect_timeout': 1000}, pool_pre_ping=True)
    '''
    Session = sessionmaker(bind=engine)
    session = Session()
    '''
    session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))
    return session

def get_patterns(session):
    '''Get the values in the database for the searchterm to match against
    Returns
        patterns_values - a 1-D list of patterns.values (name, synonym, product,
                            name, synonym, product ...)
        patterns - a dict containing the unflattened values in patterns_values
    '''
    patterns = ({'Name': [row.name for row in session.query(Name.name)],
                 'Synonym': [row.synonym for row in session.query(Synonym.synonym)],
                 'Product': [row.product for row in session.query(Product.product)]})


    # Flatten pattern.values()
    patterns_values = []
    for sublist in patterns.values():
        for item in sublist:
            patterns_values.append(item)

    patterns_values = [i.lower() for i in patterns_values]
    return patterns_values, patterns

def get_userinput():
    '''Get user input'''
    userinput = input('Search:').lower().strip()
    return userinput

class Query():
    def __init__(self, session, pattern_values, patterns):
        # Session and patterns need to be initialised outside of the class before 
        # calling get_results()
        self.session = session
        self.pattern_values, self.patterns = pattern_values, patterns

    def get_drugname(self, searchterm, patterns_values, patterns):
        '''Compares search term with drug names (generic, synonym, or product) 
            in the database and returns best match.

        Args
            searchterm - user input
            patterns_values - flat list of names, synonyms and products
            patterns - dict of patterns_values 

        Returns
            matched_name - matched name in table (may not be original user input)
            table - table containing the matched name (determine whether input is Name,
                    Synonym, or Product)
            suggestions - a list of similar matches 
        '''
        print('searchterm:', searchterm)
        table = ''
        suggestions = None
        if searchterm not in patterns_values:
            # Return name with highest similarity score
            similarities = {}
            for value in patterns_values:
                similarity = fuzz.token_sort_ratio(value.lower(), searchterm.lower())
                #print(pattern.lower(), searchterm.lower(), similarity)
                similarities.update({value.lower(): similarity})
            matched_name =  max(similarities, key = similarities.get)
            max_similarity = max(similarities.values())
            print('Similarity:', max_similarity)
            # Provide a few similar patterns at intervals from max
            suggestions = sorted(similarities,
                                    key = similarities.get, reverse = True)[:10:2]
            # Capitalise similar product names
            suggestions = [i.capitalize() for i in suggestions]
            print('Did you mean:', matched_name, '?')
            print('Other suggestions:', suggestions)
        else:
            matched_name = searchterm
        # Get key
        for item in patterns.items():
            # items() returns tuples of key-value pairs
            if matched_name in [i.lower() for i in item[1]]:
                table = item[0]
                # Stop iterating if found earlier e.g. in 'Name'
                break

        print('Matched:', matched_name)
        print('Table:', table)
        return matched_name, table, suggestions

    def query(self, searchterm, table, session):
        '''Finds the drugbank ID and uses it to look up all associated data.
        Args
            searchterm - matched drug name
            table - table containing matched name (Name, Synonym, or Product)
            session - DB session
        Returns
            dict containing all associated data for matched drug

        '''
        
        drugbank_id = ''
        print(searchterm)
        if searchterm:
            # Attempt to query the db
            for i in range(0, 10):
                try:
                    if table == 'Name':
                        drugbank_id = (session.query(Name.drugbank_id)
                                    .filter(Name.name.ilike(searchterm))
                                    .all())
                    elif table == 'Synonym':
                        drugbank_id = (session.query(Synonym.drugbank_id)
                                    .filter(Synonym.synonym.ilike(searchterm))
                                    .all())
                    elif table == 'Product':
                        drugbank_id = (session.query(Product.drugbank_id)
                                    .filter(Product.product.ilike(searchterm))
                                    .all())

                    # If product contains multiple ingredients:
                    for i in drugbank_id:
                        print('---\ndrugbank_id:', i[0])
                        name = (session.query(Name.name)
                                .filter(Name.drugbank_id == i[0]).all()[0][0])
                        d_class = (session.query(Pharm.d_class)
                                .filter(Pharm.drugbank_id == i[0]).all()[0][0])
                        ind = (session.query(Pharm.ind)
                            .filter(Pharm.drugbank_id == i[0]).all()[0][0])
                        pd = (session.query(Pharm.pd)
                            .filter(Pharm.drugbank_id == i[0]).all()[0][0])
                        mech = (session.query(Pharm.mech)
                                .filter(Pharm.drugbank_id == i[0]).all()[0][0])
                        # Synonyms and products are lists
                        synonyms = (session.query(Synonym.synonym)
                                    .filter(Synonym.drugbank_id == i[0]).all())
                        products = (session.query(Product.product)
                                    .filter(Product.drugbank_id == i[0]).all())
                except exc.InvalidRequestError:
                    session.rollback()
                    continue
                break
            
        #return drugbank_id, name, d_class, ind, pd, mech, synonyms, products, suggestions
        return dict(drugbank_id=drugbank_id, 
                    name=name, d_class=d_class, ind=ind, pd=pd, mech=mech, synonyms=synonyms, products=products)

    def get_results(self, searchterm):
        '''Returns drug name with all associated data given a search input. 
        This function combines get_drugname and query.

        Args
            searchterm - user input
        
        Returns
            results - dict containing drug data
        '''        
        
        matched_name, table, suggestions = self.get_drugname(searchterm, self.pattern_values, self.patterns)
        print('matched_name:', matched_name)
        results = self.query(matched_name, table, self.session)
        results['suggestions'] = suggestions
        
        self.session.close()
        return results

def stringify(obj):
    '''Turn synonym and product objects into strings'''
    stringified = []
    if obj:
        for i in obj:
            stringified.append(i[0])
        stringified = ', '.join(stringified)
    return stringified


if __name__ == '__main__':
    # Connect to db and get patterns to match against on startup
    session = db_session()
    searchterm = get_userinput()
    pattern_values, patterns = get_patterns(session)
    #results = get_results(searchterm, patterns_values, patterns, session)
    query = Query(session, pattern_values, patterns)
    results = query.get_results(searchterm)
    
    print('Name:', results['name'], '\n')
    print('Class:', results['d_class'], '\n')
    print('Indication:', drop_tags(results['ind']), '\n')
    print('Pharmacodynamics:', drop_tags(results['pd']), '\n')
    print('Mechanism of action:', drop_tags(results['mech']), '\n')
    print('Synonyms:')
    for synonym in results['synonyms']:
        if synonym[0] != results['name']:
            print(synonym[0], end = ' | ')
    print('\nFound in:')
    for product in results['products']:
        # This is a very long list
        #print(product[0], end = ', ')
        pass

    
    
