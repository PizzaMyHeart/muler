# Muler

Muler is a Flask app that allows users to search for pharmacological information by generic or proprietary drug names. The information is sourced from a DrugBank dataset under a CC BY-NC 4.0 license. 

Requires an sqlite3 database 'muler.db' in /app/database/

## Running Muler:

1. Enter the 'app' directory

```
cd <basedir>/app
```

2. Start the Flask server

```
flask run 
```

Add ```--host 0.0.0.0:<port>``` to access the app from other devices on the local network.
Note that use of the Flask server in production is strongly discouraged. 

Instead of using Flask, you can also run Muler as a command-line script from the 'app' directory.

```
python3 -m database.query
```


TODO

- Search db
  - Levenshtein distance (spellfix/editdist3) [DONE]
  - Autocomplete.js

- Flask app 
  - HTML form validation
    - Remove trailing whitespace
  - Update test.db to use same schema as muler.db
  - CSS
    - Remove borders on searchbar focus on mobile

- Update rofecoxib and mephenytoin mechanism of action [DONE]
- Approved/withdrawn/investigational (Groups)
