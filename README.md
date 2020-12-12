# Muler

Muler is a Flask app that allows users to search for pharmacological information by generic or proprietary drug names. The information is sourced from a DrugBank dataset under a CC BY-NC 4.0 license. 

Requires an sqlite3 database 'muler.db' in /app/database/



TODO
- XML parser [DONE]
- Write to db [DONE]
- Search db
  - Levenshtein distance (spellfix/editdist3) [DONE]
  - Autocomplete.js
- Regex sanitiser
  - Drop brackets [DONE]
  - Strip trailing whitespace [DONE]
- Flask app 
- Synonyms e.g. aspirin = acetylsalicylic acid, paracetamol = acetaminophen [DONE]
- Indication [DONE]
- Drug class (<atc-codes>) [DONE]
- Brand names (<products>) [DONE]
- Update rofecoxib and mephenytoin mechanism of action [DONE]
- Approved/withdrawn/investigational (Groups)
