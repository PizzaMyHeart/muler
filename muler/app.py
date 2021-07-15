#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for
from muler.database import regex
import markdown
import muler.query as query

session = query.db_session()
patterns_values, patterns = query.patterns(session)

def search(searchterm):

    results = query.get_results(searchterm, patterns_values, patterns, session)
    lambda x: markdown.markdown([results[x] for x in ['ind', 'pd', 'mech']])
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


def get_userinput():
    userinput = request.form['search'].lower().strip()
    return userinput

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
        '''Queries the database via search() using the url slug 
        '''
        if request.method == 'POST':    # Searching while on a result page
            return redirect(url_for('link', link=get_userinput()))

        return search(link.lower())
    
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            return redirect(url_for('link', link=get_userinput()))        
        elif request.method == 'GET':    
            return render_template('index.html')
    
    return app
