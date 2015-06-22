from flask import Flask
from flask import render_template, redirect, request, url_for
from elasticsearch import Elasticsearch
import re
from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

app = Flask(__name__)

@app.errorhandler(500)
def search_failed(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# for WTForms. I can get rid of this if I don't move to them.
app.config.from_object('config')

es = Elasticsearch()

results = {}
search_query = ""

def search(healthy_volunteer_filter, gender_filter):
    query = get_search_query()
    if(healthy_volunteer_filter):
        query = query + " AND healthy_volunteers:" + healthy_volunteer_filter
        set_search_query(query)
    if(gender_filter):
        query = query + " AND gender:" + gender_filter
        set_search_query(query)
    search = es.search(index="clinical_trials", body={"query":{"query_string":{"query": query}},"aggs":{"healthy_volunteer":{"terms":{"field":"healthy_volunteers"}},"gender":{"terms":{"field":"gender"}}},"highlight": {"fields": {"official_title": {"number_of_fragments": 0},"detailed_description":{"number_of_fragments":0},"eligibility":{"number_of_fragments":0}}}}, size=500)
    set_results(search)
    return get_results()

def set_search_query(query):
    global search_query
    search_query = query

def get_search_query():
    return search_query

def set_results(search):
    global results
    results = search

def get_results():
    return results

@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        search_term = request.form['search']
        set_search_query(search_term)

        return redirect(url_for('search_results', query=search_term))
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/search_results/<query>', methods=['GET', 'POST'])
def search_results(query):
    healthy_volunteer_filter = request.args.get("healthy_volunteer_filter")
    gender_filter = request.args.get("gender_filter")

    if request.method == 'POST':
        search_term = request.form['search']
        set_search_query(search_term)

        return redirect(url_for('search_results', query=search_term))
    if request.method == 'GET':
        search_results = search(healthy_volunteer_filter, gender_filter)

        return render_template('search_results.html', query=query, search_results=search_results)

@app.route('/help', methods=['GET', 'POST'])
def help():
    if request.method == 'POST':
        search_term = request.form['search']

        return redirect(url_for('search_results', query=search_term))
    if request.method == 'GET':
        return render_template('help.html', page='help')

@app.route('/about')
def about():
    return render_template('about.html', page='about')

@app.route('/contact')
def contact():
    return render_template('contact.html', page='contact')

@app.route('/trial/<id>')
def trial(id):
    trial_results = get_results()

    for i in range(len(trial_results['hits']['hits'])):
        if trial_results['hits']['hits'][i]['_id'] == id:
            trial = trial_results['hits']['hits'][i]
            overall_status = trial_results['hits']['hits'][i]['_source']['overall_status']

    if overall_status == "Recruiting":
        alert = 'alert alert-success'
    elif overall_status == 'Active, not recruiting':
        alert = 'alert alert-error'
    elif overall_status == 'Completed':
        alert = 'alert alert-error'
    else:
        alert = 'alert alert-block'

    return render_template('trial.html', trial=trial, id=id, alert=alert)

if __name__ == '__main__':
    app.run(debug=True)
