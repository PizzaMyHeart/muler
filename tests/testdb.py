#!/usr/bin/python3
"""Create a sample database for testing

Quick and dirty script to create a sample database from muler.db for testing.
Contains information for first 20 drugs in the DrugBank dataset.

Move the generated test.db to /app/database/ before running app.py or query.py
"""

import sqlite3

db = "test.db"

conn = sqlite3.connect(db)
cur = conn.cursor()

# Fetch first 20 rows in name table
cur.execute("SELECT * FROM name")
twenty = cur.fetchmany(20)



def select_20(table, drugbank_ids):
	# Fetch 20 matching rows
	cur.execute("SELECT * FROM {} WHERE drugbank_id IN {}".format(table, str(tuple(drugbank_ids))))
	return cur.fetchall()


def delete_rows(table):
	# Delete all rows
	cur.execute(f'DELETE FROM {table}')


# Replace name table with 20 matching rows
delete_rows("name")
cur.executemany("INSERT INTO name VALUES (?, ?)", twenty)



drugbank_ids = [i[0] for i in twenty]



# Pharm table
rows = select_20("pharm", drugbank_ids)
delete_rows("pharm")
cur.executemany("INSERT INTO pharm VALUES (?, ?, ?, ?, ?)", rows)

# Synonym table
rows = select_20("synonym", drugbank_ids)
delete_rows("synonym")
cur.executemany("INSERT INTO synonym VALUES (?, ?)", rows)

# Product table
rows = select_20("product", drugbank_ids)
delete_rows("product")
cur.executemany("INSERT INTO product VALUES (?, ?)", rows)



conn.commit()
conn.close()