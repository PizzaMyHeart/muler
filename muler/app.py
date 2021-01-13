#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for
from muler.database import regex
import markdown
import muler.query as query

session = query.db_session()
patterns_values, patterns = query.patterns(session)

def search(search):

    results = query.get_results(search, patterns_values, patterns, session)
    results['ind'] = markdown.markdown(results['ind'])
    results['pd'] = markdown.markdown(results['pd'])
    results['mech'] = markdown.markdown(results['mech'])
    session.close()
    return render_template('result.html',
                           results=results,
                           drugbank_id=results['drugbank_id'],
                           name=results['name'],
                           d_class=results['d_class'],
                           ind=regex.drop_tags(results['ind']),
                           pd=regex.drop_tags(results['pd']),
                           mech=regex.drop_tags(results['mech']),
                           synonyms=query.stringify(results['synonyms']),
                           products=query.stringify(results['products']),
                           suggestions=results['suggestions'])


def create_app(test_config=None):

 
    app = Flask(__name__, instance_relative_config=True)
    
    @app.route('/about')
    def about():
      return render_template('about.html')

    @app.route('/legal')
    def legal():
      return render_template('legal.html')

    @app.route('/<link>', methods=['GET', 'POST'])
    def link(link):
        if request.method == 'POST':
            userinput = request.form['search'].lower()
            return redirect(url_for('link', link=userinput))

        return search(link.lower())
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            userinput = request.form['search'].lower()
            return redirect(url_for('link', link=userinput))        
        elif request.method == 'GET':    
            return render_template('index.html')
    
    return app