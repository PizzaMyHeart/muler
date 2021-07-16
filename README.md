# Muler

Muler is a Flask app that allows users to search for pharmacological information by generic or proprietary drug names. The information is sourced from a DrugBank [dataset](https://go.drugbank.com/releases/latest) under a [CC BY-NC 4.0 license](https://creativecommons.org/licenses/by-nc/4.0/legalcode). The original dataset is a fairly large XML file, which has been processed into ~~an SQLite database~~ a MySQL database using a Python script. 

![Home page](/search.png?raw=true "Home page")

![Results page](/result.png?raw=true "Results page")


## Running Muler locally

1. Enter the 'muler' directory

```
cd <basedir>/muler
```

2. Start the Flask server

```
flask run 
```

Add ```--host 0.0.0.0:<port>``` to access the app from other devices on the local network.
Note that use of the Flask server in production is strongly discouraged. 

Instead of using Flask, you can also run Muler as on the command line from the base directory.

```
python3 -m muler.query
```

## Deploying to PythonAnywhere
*[General method](https://help.pythonanywhere.com/pages/Flask/) to deploy Flask app on PythonAnywhere.*

1. Pull from ```origin/master```.
```
git stash
git stash drop
git pull
```
WARNING: This will destroy local changes.

2. Update ```sys.path``` and imports in WSGI config if needed.
Current config with muler set up as a package:
```
path = '/home/muler/muler'  # /home/<username>/<basedir>
if path not in sys.path:
    sys.path.append(path)
# Import applciation factory
from muler.app import create_app
application = create_app()
```

3. Upload config.py (contains database paths), which is untracked by Git. Make sure it's located in ```/home/muler/muler/muler/``` (I know, *sigh*).

TODO

- Search db
  - Levenshtein distance (spellfix/editdist3) [DONE]
  - Autocomplete.js

- Flask app 
  - HTML form validation
    - Remove trailing whitespace [DONE]
  - CSS
    - Remove borders on searchbar focus on mobile

- Update rofecoxib and mephenytoin mechanism of action [DONE]
- Approved/withdrawn/investigational (Groups)



## Changelog

### 2021-01-12
- Migrated from SQLite to MySQL using sqlite3-to-mysql.py

### 2021-07-16
- Input sanitisation and minor optimisations for faster response time (not formally measured)