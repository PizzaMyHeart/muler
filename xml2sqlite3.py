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

cur.execute('DROP TABLE IF EXISTS moa')
cur.execute('''
    CREATE TABLE IF NOT EXISTS moa (
        drugbank_id text PRIMARY KEY,
        name text NOT NULL,
        pd text, 
        mechanism text)
''')


tree = ET.iterparse(source, events = ('start', 'end'))

# Get root element
event, root = next(tree)

def parse_xml():
    '''
    Iterates over the element tree and returns drug name and mechanism of action.
    Uses root.clear() instead of elem.clear() (see http://effbot.org/zone/element-iterparse.htm)
    

    Returns a 2-D list of drug entries.
    '''
    # We only want immediate child elements of each entry (depth == 1)
    depth = 0
    # Outermost container
    drugbank = []
    # Inner container
    drugs = []
    index = ''
    for event, elem in tree:
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
                    print('Drugbank id:', elem.text, '\n')
                    matched = elem.text
                    index = elem.text
                elif elem.tag == '{http://www.drugbank.ca}name':
                    print('Drug name:', elem.text, '\n')
                    matched = elem.text
                elif elem.tag == '{http://www.drugbank.ca}pharmacodynamics':
                    print('Pharmacodynamics:', elem.text, '\n')
                    matched = elem.text
                elif elem.tag == '{http://www.drugbank.ca}mechanism-of-action':
                    print('Mechanism of action:', elem.text, '\n---\n')
                    matched = elem.text
                if matched == None:
                    matched = 'NA'
                if matched:    
                    print('Item matched:', matched, '\n')
                    # If new index, append current list to drugbank and reset
                    if index not in drugs and drugs:
                        drugbank.append(drugs)
                        drugs = []
                    drugs.append(matched)
        # Clear current element from memory before moving on to next
        root.clear()
        
    return drugbank
        

def insert_sql(row):
    '''
    Insert one row into the "moa" table
    '''
    cur.execute('INSERT INTO moa VALUES (?, ?, ?, ?)', row)
    
# Rows to be inserted into "moa" table    
rows = parse_xml()

print('No. of rows:', len(rows))

for row in rows:
    insert_sql(row)

conn.commit()
