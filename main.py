from flask import Flask
from flask import render_template
from flask import request
import json
import urllib.error
import urllib.parse
import urllib.request
import ssl
import os

from secrets import API_KEY

#if not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
ssl._create_default_https_context = ssl._create_unverified_context

functions = {
    'Chinese sign of year': 'findChineseSignOfYear',
    'Chinese sign of month': 'findChineseSignOfMonth',
    'Chinese sign of day': 'findChineseSignOfDay',
    'astrological enemy': 'findAstrologicalEnemy',
    'secret friend': 'findSecretFriend',
}

def safe_get(url):
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read()
        return json.loads(data)
    except urllib.error.HTTPError as e:
        print('Error trying to retrieve astrological data. Error code: {}'.format(e.code))
    except urllib.error.URLError as e:
        print('We failed to reach a server.\nReason: {}'.format(e.reason))
    return None

def AstroREST(base_url='https://fengshui-api.com/api/v1/',
              func='findChineseSignOfYear',
              api_key=API_KEY,
              params={},
              printurl=False):
    params['token'] = api_key
    url = '{}{}?{}'.format(base_url, func, urllib.parse.urlencode(params))

    if printurl:
        print(url)
    else:
        return safe_get(url)

app = Flask(__name__)

@app.route('/')
def home():
    vals = {
        'page_title': 'Birthday Form'
    }
    return render_template('astro_form.html', vals=vals)

@app.route('/result', strict_slashes=False)
def results():
    vals = {
        'page_title': 'Astro Info Printout',
    }
    year = request.args.get('year')
    month = request.args.get('month')
    day = request.args.get('day')

    if year and month and day:
        vals['year'] = year
        vals['month'] = month
        vals['day'] = day
        astro_info = {}
        for func in functions:
            #astro_info[functions[func]] = AstroREST(func=func, params=vals)['result']
            astro_info[functions[func]] = {}
            astro_info[functions[func]].update(AstroREST(func=functions[func], params=vals))
            astro_info[functions[func]]['phrase'] = func
        vals['astro_info'] = astro_info
        print(astro_info)
        return render_template('astro_response.html', vals=vals)
    else:
        vals['prompt'] = 'Please enter all parts of your birthday (month, day, year)'
        return render_template('astro_form.html', vals=vals)

if __name__ == '__main__':
    app.run('127.0.0.1', port=8080, debug=True)
