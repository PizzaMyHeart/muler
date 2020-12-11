#!/usr/bin/python3


import os.path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fuzzywuzzy import fuzz
from database.models import Pharm, Name, Synonym, Product
from database.regex import drop_tags

def db_session():

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, 'muler.db')
    db_url = 'sqlite:///' + db_path + '?check_same_thread=False'

    engine = create_engine(db_url, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session

def patterns(session):

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

def userinput():
    '''
    Get user input
    '''
    userinput = input('Search:').lower()
    return userinput


def get_results(search, patterns_values, patterns, session):
    def get_search(search, patterns_values, patterns):
        '''
        Takes user input and matches it against rows in name column

        Args
            search - user input
            patterns_values - flat list of names, synonyms and products

        Returns
            querystring - matched name in table
            table - table containing the matched name
        '''
        table = ''
        suggestions = None
        while True:
            #search = input('Search:').lower()
            if search == 'quit':
                break
            if search == '':
                print('Please enter a search term.')
                continue
            if search == 'na':
                print('No results found.')
                return False


            if search not in patterns_values:
                # Return name with highest similarity score
                similarities = {}
                for value in patterns_values:
                    similarity = fuzz.token_sort_ratio(value.lower(), search.lower())
                    #print(pattern.lower(), search.lower(), similarity)
                    similarities.update({value.lower(): similarity})
                search =  max(similarities, key = similarities.get)
                max_value = max(similarities.values())
                print('Similarity:', max_value)
                # Provide a few similar patterns at intervals from max
                suggestions = sorted(similarities,
                                     key = similarities.get, reverse = True)[:10:2]
                # Capitalise similar product names
                suggestions = [i.capitalize() for i in suggestions]
                print('Did you mean:', search, '?')
                print('Other suggestions:', suggestions)
            
            # Get key
            for item in patterns.items():
                # items() returns tuples of key-value pairs
                if search in [i.lower() for i in item[1]]:
                    table = item[0]
                    # Stop iterating if found earlier e.g. in 'Name'
                    break



            print('Matched:', search)
            print('Table:', table)
            return search, table, suggestions



    def query(search, table, session):
        '''

        '''
        
        drugbank_id = ''
        if search:
            if table == 'Name':
                drugbank_id = (session.query(Name.drugbank_id)
                               .filter(Name.name.ilike(search))
                               .all())
            elif table == 'Synonym':
                drugbank_id = (session.query(Synonym.drugbank_id)
                               .filter(Synonym.synonym.ilike(search))
                               .all())
            elif table == 'Product':
                drugbank_id = (session.query(Product.drugbank_id)
                               .filter(Product.product.ilike(search))
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
            
            print('Name:', name, '\n')
            print('Class:', d_class, '\n')
            print('Indication:', drop_tags(ind), '\n')
            print('Pharmacodynamics:', drop_tags(pd), '\n')
            print('Mechanism of action:', drop_tags(mech), '\n')
            print('Synonyms:')
            for synonym in synonyms:
                if synonym[0] != name:
                    print(synonym[0], end = ' | ')
            print('\nFound in:')
            for product in products:
                #print(product[0], end = ', ')
                pass
        return drugbank_id, name, d_class, ind, pd, mech, synonyms, products, suggestions
    
    search, table, suggestions = get_search(search, patterns_values, patterns)
    results = query(search, table, session)
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
    session = db_session()
    patterns_values, patterns = patterns(session)
    search = userinput()
    results = get_results(search, patterns_values, patterns, session)
    
    
