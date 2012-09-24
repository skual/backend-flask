# coding=utf-8

from flask import Flask, redirect, g, request

import configs
from routes import urls
from session import session_store

app = Flask(__name__, **configs.instance)
app.config.update(configs.project)

# We now define basics routes to ensure that the user is well redirected to the frontend
@app.before_request
def before_request():
    g.session = session_store.get(request)

@app.route('/', methods=['GET',])
def index():
    """
    Redirect to the frontend's index.html view
    """
    return redirect('/s/index.html')

@app.route('/s/', methods=['GET',])
def index_static():
    """
    Redirect to the frontend's index.html view
    """
    return redirect('/s/index.html')

@app.route('/favicon.ico', methods=['GET',])
def favicon():
    """
    We don't want to use resources just for a favicon
    that will be well indicated in the html
    so we return a 404
    """
    return ("", 404)

# And we import the urls :
for url in urls:
    app.add_url_rule(url.path, **url.options)

# And we run the instance
if __name__ == '__main__':
    app.run()