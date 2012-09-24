# coding=utf-8

from flask import jsonify, request, g
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from time import mktime

import uuid
import urllib

from session import session_store
from decorators import requires, authenticated

@requires('username', 'server-engine', 'server-hostname', 'server-port')
def connect():
    """
    Test the given login/password agains't the database
    If it's ok, save them encrypted in the session
    and return the state of the connection
    """
    try:
        values = {
            'engine':   request.form['server-engine'],
            'username': urllib.quote_plus(request.form['username']),
            'password': urllib.quote_plus(request.form['password']) if 'password' in request.form else '',
            'host':     urllib.quote_plus(request.form['server-hostname']),
            'port':     int(request.form['server-port'])
        }

        cnx = create_engine('%s://%s:%s@%s:%d' % (
                                values['engine'],
                                values['username'],
                                values['password'],
                                values['host'],
                                values['port'],
                            ))
        cnx.connect()

        token = uuid.uuid4().hex
        g.session = session_store.create(request, token, values)
        
        return jsonify({
            'token': token,
            'expire': mktime(g.session.expire.timetuple())
        })
    except OperationalError as e:
        response = jsonify ({'code': e.orig[0], 'message': e.orig[1]})
        response.status_code = 400
        return response

def disconnect():
    if 'session' in g.__dict__:
        g.session = None
        session_store.clear(request)

    return ('', 200);

@authenticated
def test():
    return "Yay"