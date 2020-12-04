#!/usr/bin/python3

'''xml2sqlite3
This script iteratively parses an XML file and stores elements of interest
in a 2-D list. The list is then inserted into an sqlite database.

There are two functions: 
    * parse_xml - iteratively parse XML
    * insert_sql - insert a row into the sqlite db
'''

import xml.etree.ElementTree as ET
import sqlite3

source = 'database.xml'
database = 'muler.db'

conn = sqlite3.connect(database)
cur = conn.cursor()


def create_table(table, columns):
    '''
    Creates SQL table with corresponding columns
    '''
    cur.execute(f'DROP TABLE IF EXISTS {table}')
    columns = ', '.join(columns)
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS {table} (
            {columns});
    ''')
    print(table, 'created')

create_table('pharm', ['drugbank_id text PRIMARY KEY',
                       'pd text', 'mech text', 'ind text', 'd_class text'])
create_table('name', ['drugbank_id text PRIMARY KEY',
                      'name text'])
create_table('synonym', ['drugbank_id text', 'synonym text', 
                         'FOREIGN KEY (drugbank_id) REFERENCES name(drugbank_id)'])
create_table('product', ['drugbank_id text', 'product text', 
                         'FOREIGN KEY (drugbank_id) REFERENCES name(drugbank_id)'])

# Turn XML file into iterable
tree = ET.iterparse(source, events = ('start', 'end'))

# Get root element
event, root = next(tree)


def parse_moa():
    '''
    Iterates over the element tree and returns drug name and mechanism of action.
    Uses root.clear() instead of elem.clear() (see http://effbot.org/zone/element-iterparse.htm)
    

    Returns a 2-D list of drug entries.
    '''
    print('Parsing...')
    n = 0
    # We only want immediate child elements of each entry (depth == 1)
    depth = 0
    # Outermost container
    drugbank = []
    # Inner container
    drugs = []
    index = ''
    for event, elem in tree:
        if n == 50000:
            pass
        matched  = ''        
        if event == 'start':
            depth += 1
        if event == 'end':
            depth -= 1
        if depth == 1:
            # Wait for closing tag
            if event == 'end':
                # Get drugbank-id tags with attribute 'primary'
                if (elem.tag == '{http://www.drugbank.ca}drugbank-id' and
                      elem.items() == [('primary', 'true')]):
                    #print('Drugbank id:', elem.text, '\n')
                    matched = elem.text
                    # Use this as index to track progress through tree
                    index = elem.text
                elif elem.tag == '{http://www.drugbank.ca}name':
                    #print('Drug name:', elem.text, '\n')
                    matched = elem.text
                elif elem.tag == '{http://www.drugbank.ca}pharmacodynamics':
                    #print('Pharmacodynamics:', elem.text, '\n')
                    matched = elem.text
                elif elem.tag == '{http://www.drugbank.ca}mechanism-of-action':
                    #print('Mechanism of action:', elem.text)
                    matched = elem.text
                elif elem.tag == '{http://www.drugbank.ca}indication':
                    #print('Indication:', elem.text, '\n---\n')
                    matched = elem.text
                # Drug class
                elif elem.tag == '{http://www.drugbank.ca}atc-codes':
                    if elem:
                        #print('Drug class:', elem[0][0].text)
                        matched = elem[0][0].text
                    else:
                        matched = 'NA'
                elif elem.tag == '{http://www.drugbank.ca}synonyms':
                    if elem:
                        matched = [child.text for child in elem] 
                        #print('Synonyms:', matched)
                    else:
                        matched = 'NA'
                elif elem.tag == '{http://www.drugbank.ca}products':
                    if elem:
                        # Add only if still marketed
                        matched = [child[0].text for child in elem
                                   if child[8].text == None]
                        #print('Products:', matched)
                    else:
                        matched = 'NA'
                if matched == None:
                    matched = 'NA'
                if matched:    
                    #print('Item matched:', matched, '\n')
                    # If new index, append current list to drugbank and reset
                    if index not in drugs and drugs:
                        drugbank.append(drugs)
                        drugs = []
                    drugs.append(matched)
        # Clear current element from memory before moving on to next
        root.clear()
        n += 1
    print('Parsing complete.')
    return drugbank


parsed = parse_moa()


def sort_parsed(parsed):
    '''
    Process parsed results into separate lists for each table to be 
    inserted into

    Indices:
    0 - drugbank_id
    1 - name
    2 - indication
    3 - pd
    4 - mech
    -3 / 5 - synonym 
    -2 / 6 - product
    -1 / 7 - d_class
    '''
    pharm_rows, name_rows, synonym_rows, product_rows = [], [], [], []
    print('Parsed: \n')
    for drug in parsed:
        pharm_rows.append([drug[0], drug[3], drug[4], drug[2], drug[-1]])
        name_rows.append([drug[0], drug[1]])
        synonym_rows.append([drug[0], drug[-3]])
        # Unique product values only
        product = drug[-2]
        if type(product) == list:
            product = list(set(product))
        product_rows.append([drug[0], product])
        #print(drug, '\n------')
        #print(product_rows)
        #print('\n')
    #print('pharm_rows:', len(pharm_rows), 'rows')
    #print('name_rows:', len(name_rows), 'rows')
    #print('synonym_rows:', len(synonym_rows), 'rows')
    #print('product_rows:', len(product_rows), 'rows')
    #print('product:', product_rows[-1])
    return pharm_rows, name_rows, synonym_rows, product_rows

pharm_rows, name_rows, synonym_rows, product_rows = sort_parsed(parsed)
        
def split_lists(rows):
    '''
    Split product and synonym fields that contain lists
    rows 

    Returns
        split - list containing rows that have been split into lists with 2 
                items
    '''
    split = []
    for row in rows:
        # row[1] must be a list
        if type(row[1]) != list:
            row[1] = [row[1]]
        for item in row[1]:
            split.append([row[0], item])
    return split
    
def insert_sql(rows, table):
    '''
    Insert preprocessed rows into the "moa" table
    rows - list of preprocessed rows
    table 
    '''
    for row in rows:
        tokens = ['?'] * len(row)
        tokens = ', '.join(tokens)
        cur.execute(f'INSERT INTO {table} VALUES ({tokens})', row)
    



# Split product_rows and synonym_rows
synonym_rows = split_lists(synonym_rows)
product_rows = split_lists(product_rows)

insert_sql(pharm_rows, 'pharm')
insert_sql(name_rows, 'name')
insert_sql(synonym_rows, 'synonym')
insert_sql(product_rows, 'product')

conn.commit()
conn.close()
