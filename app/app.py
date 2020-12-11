#!/usr/bin/python3

import os
from flask import Flask, render_template, request, redirect, url_for
from database import query, regex
import markdown

session = query.db_session()
patterns_values, patterns = query.patterns(session)

def search(search):

    results = query.get_results(search, patterns_values, patterns, session)
    drugbank_id, name, d_class, ind, pd, mech, synonyms, products, suggestions = results
    ind = markdown.markdown(ind)
    pd = markdown.markdown(pd)
    mech = markdown.markdown(mech)
    return render_template('result.html',
                           results=results,
                           drugbank_id=drugbank_id,
                           name=name,
                           d_class=d_class,
                           ind=regex.drop_tags(ind),
                           pd=regex.drop_tags(pd),
                           mech=regex.drop_tags(mech),
                           synonyms=query.stringify(synonyms),
                           products=query.stringify(products),
                           suggestions=suggestions)


def create_app(test_config=None):
 
    app = Flask(__name__, instance_relative_config=True)

    @app.route('/about')
    def about():
      #return render_template('about.html')
      return 'Under construction'

    @app.route('/<link>', methods=['GET', 'POST'])
    def link(link):
        if request.method == 'POST':
            userinput = request.form['search'].lower()
            return redirect(url_for('link', link=userinput))
            #return search(request.form['search'])
            
        return search(link.lower())
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            userinput = request.form['search'].lower()
            return redirect(url_for('link', link=userinput))
            #return search(request.form['search'])            
        elif request.method == 'GET':    
            return render_template('index.html')

    return app
