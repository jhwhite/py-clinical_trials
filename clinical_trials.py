from flask import Flask
from flask import render_template, redirect, request, url_for
from elasticsearch import Elasticsearch
import re
from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

app = Flask(__name__)

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

@app.errorhandler(500)
def search_failed(e):
    return render_template('500.html'), 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# for WTForms. I can get rid of this if I don't move to them.
app.config.from_object('config')

es = Elasticsearch()

def search(search_term):
    index = "clinical_trials"
    search_results = es.search(index=index, body={"query":{"match":{ "official_title": search_term}}}, size=500)
    return search_results

# search query


@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        search_term = request.form['search']

        return redirect(url_for('search_results', query=search_term))
    if request.method == 'GET':
        return render_template('index.html')

@app.route('/search_results/<query>', methods=['GET', 'POST'])
def search_results(query):
    if request.method == 'POST':
        search_term = request.form['search']

        return redirect(url_for('search_results', query=search_term))
    if request.method == 'GET':

        search = {
            "query":{
                "query_string":{
                    "query": query
                    }
                },
                "aggs":{
                    "healthy_volunteer":{
                        "terms":{
                            "field":"healthy_volunteers"
                        }
                    },
                    "gender":{
                        "terms":{
                            "field":"gender"
                        }
                    }
                }
            }

        results = es.search(index="clinical_trials", body=search, size=500)
        num_hits = results['hits']['total']

        return render_template('search_results.html', query=query, results=results, num_hits=num_hits)

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
    results = es.get(index='clinical_trials', doc_type='trial', id=id)

    overall_status = results['_source']['overall_status']

    if overall_status == "Recruiting":
        alert = 'alert alert-success'
    elif overall_status == 'Active, not recruiting':
        alert = 'alert alert-error'
    elif overall_status == 'Completed':
        alert = 'alert alert-error'
    else:
        alert = 'alert alert-block'

    return render_template('trial.html', results=results, alert=alert)

if __name__ == '__main__':
    app.run()
