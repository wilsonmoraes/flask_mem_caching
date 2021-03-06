import json
from datetime import datetime

import requests
from flask import Flask, Response, request
from flask_caching import Cache

config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
APP_ID = "7ff34241554a082a05efc8f7f30320ea"
PATH_OPEN_API = "http://api.openweathermap.org/data/2.5/weather"

app = Flask(__name__)
app.config.from_mapping(config)
cache = Cache(app)


@app.route('/health')
@cache.cached(300)
def health_check():
    return "It's Working"


@app.route('/weather/')
def list_weather_with_size():
    params = request.args.to_dict()
    max_number = params.get('max_number', 5)
    last_cached_items = {}
    for ind, item in enumerate(cache.cache.cache):
        last_cached_items[item] = cache.get(item)
        if ind == max_number:
            break
    return Response(json.dumps(last_cached_items), mimetype='application/json', status=200)


@app.route('/weather/<city_name>')
# @cache.cached(timeout=10, key_prefix='cached_cities')
def list_weather(city_name):
    query_string = {'q': city_name, 'appid': APP_ID}
    resp = requests.get(PATH_OPEN_API, params=query_string)
    cache.set(city_name, json.loads(resp.text), timeout=5 * 60)
    return Response(resp.text, mimetype='application/json', status=resp.status_code)


app.debug = True
app.run(port=5000, debug=True, host='0.0.0.0')
