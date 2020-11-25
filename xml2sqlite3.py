#!/usr/bin/python3

import xml.etree.ElementTree as ET

source = 'database.xml'

tree = ET.iterparse(source, events = ('start', 'end'))

# Get root element
event, root = next(tree)

def xml_parser():
    '''
    Iterates over the element tree and returns drug name and mechanism of action.
    Uses root.clear() instead of elem.clear() (see http://effbot.org/zone/element-iterparse.htm)
    
    '''
    # We only want immediate child elements of each entry (depth == 1)
    depth = 0
    
    for event, elem in tree:


        if event == 'start':
            depth += 1
        if event == 'end':
            depth -= 1
        if depth == 1:
            # Wait for closing tag
            if event == 'end':
                # Match element tags
                if elem.tag == '{http://www.drugbank.ca}name':
                    print('Drug name:', elem.text, '\n')
                elif elem.tag == '{http://www.drugbank.ca}pharmacodynamics':
                    print('Pharmacodynamics:', elem.text, '\n'
                elif elem.tag == '{http://www.drugbank.ca}mechanism-of-action':
                    print('Mechanism of action:', elem.text, '\n---\n')
        # Clear current element from memory before moving on to next
        root.clear()

        
        #breakpoint()
        
     

xml_parser()


