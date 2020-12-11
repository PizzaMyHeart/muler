#!/usr/bin/python3
'''Corrects errors in db built from parsed XML
Run this after xml2sqlite3.py

'''

import sqlite3

database = 'muler.db'


infliximab = '''UPDATE pharm
                SET pd = "Infliximab disrupts the activation of pro-inflammaory cascade signalling. Infliximab has shown to reduce infiltration of inflammatory cells into sites of inflammation. It also attenautes the expression of molecules mediating cellular adhesion {including E-selectin, intercellular adhesion molecule-1 (ICAM-1) and vascular cell adhesion molecule-1 (VCAM-1)}, chemoattraction {IL-8 and monocyte chemotactic protein (MCP-1)} and tissue degradation {matrix metalloproteinase (MMP) 1 and 3} [FDA Label]." 
                WHERE drugbank_id = "DB00065";
'''

rofecoxib = '''DELETE FROM synonym
                WHERE drugbank_id = "DB00533";
               INSERT INTO synonym (drugbank_id, synonym)
                VALUES
("DB00533", "3-phenyl-4-[4-(methylsulfonyl)phenyl]-2(5H)-furanone"),
("DB00533", "4-[4-(methylsulfonyl)phenyl]-3-phenyl-2(5H)-furanone"),
("DB00533", "Rofecoxib"),
("DB00533", "Rofécoxib"),
("DB00533", "Rofecoxibum");
'''

mephenytoin = '''DELETE FROM synonym
                WHERE drugbank_id = "DB00532";
               INSERT INTO synonym (drugbank_id, synonym)
                VALUES
("DB00532", "mefenitoína"),
("DB00532", "Mephenytoin")
'''

def run_sql(sql):
    conn = sqlite3.connect(database, timeout = 5)
    print('Connection opened.')
    cur = conn.cursor()
    cur.executescript(sql)
    conn.commit()
    conn.close()
    print('Connection closed.')
    

run_sql(infliximab)
run_sql(rofecoxib)
run_sql(mephenytoin)
