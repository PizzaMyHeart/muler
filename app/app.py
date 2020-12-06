#!/usr/bin/python3

import os
from flask import Flask, render_template, request
import query
import regex

session = query.db_session()
patterns_values, patterns = query.patterns(session)



def create_app(test_config=None):
 
    app = Flask(__name__, instance_relative_config=True)


    @app.route('/')
    def index():
        
        return render_template('index.html')
        
    
    @app.route('/', methods=['POST'])
    def search():
        if request.method == 'POST':
            search = request.form['search']
            results = query.get_results(search, patterns_values, patterns, session)
            drugbank_id, name, d_class, ind, pd, mech, synonyms, products = results
            
            return render_template('index.html',
                                   results=results,
                                   drugbank_id=drugbank_id,
                                   name=name,
                                   d_class=d_class,
                                   ind=ind,
                                   pd=regex.drop_tags(pd),
                                   mech=regex.drop_tags(mech),
                                   synonyms=query.stringify(synonyms),
                                   products=query.stringify(products))
        return render_template('index.html')    
    return app
