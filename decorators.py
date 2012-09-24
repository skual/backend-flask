# coding=utf-8

from functools import wraps
from flask import request, jsonify, g

def requires(*args):
    def _required(view_func):
        def _decorator():
            errors = {}
            for key in args:
                if key not in request.args and key not in request.form:
                    if key not in errors:
                        errors[key] = []
                    errors[key].append('Required')

            if len(errors) > 0:
                return (jsonify({'code': '0100', 'message': 'Required fields are missing', 'errors': errors}), 406)

            return view_func()
        return wraps(view_func)(_decorator)
    return _required

def authenticated(view_func):
    def _decorator(*args, **kwargs):
        if 'token' not in request.args:
            return (jsonify({'disconnected': True, 'code': '0001', 'message': 'Token is required.'}), 406);
        
        if 'session' not in g.__dict__ or g.session is None:
            return (jsonify({'disconnected': True, 'code': '0000', 'message': 'Session does not exist or has expired.'}), 401);

        if not g.session.is_connected():
            return (jsonify({'disconnected': True, 'code': '0002', 'message': 'Invalid session found.'}), 401);
            
        return view_func(*args, **kwargs)

    return wraps(view_func)(_decorator)