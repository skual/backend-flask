# coding=utf-8
from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import OperationalError

import datetime
import hashlib

from utils import aes256
from configs import project

class SessionStore(object):
    def __init__(self):
        """
        Connect to SQLite
        """
        self.engine = create_engine('sqlite:///session.db')
        # Is this useful ?
        #self.db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
        self.engine.connect()
        self.engine.execute('DELETE FROM sessions WHERE expire <= ?;', datetime.datetime.now())

    def __get_browser_hash(self, request):
        return hashlib.sha1(request.remote_addr + request.headers['User-Agent']).hexdigest()

    def get(self, request):
        if 'token' not in request.args:
            return None

        result = self.engine.execute('SELECT username, password, engine, host, port, expire FROM sessions WHERE hash = ? AND token = ? and expire > ?', self.__get_browser_hash(request), request.args['token'], datetime.datetime.now())
        row = result.first()
        result.close()
        
        if row is None:
            return None
        
        values = {
            'username': row['username'],
            'password': aes256.decrypt(row['password'], self.__get_browser_hash(request) + request.args['token']),
            'engine': row['engine'],
            'host': row['host'],
            'port': row['port'],
            'expire': row['expire']
        }

        return Session(values)

    def create(self, request, token, values):
        session = self.get(request)
        if session is not None:
            return session
        
        values['expire'] = datetime.datetime.now() + datetime.timedelta(0, project['SESSION_LIFETIME'])
        browserHash = self.__get_browser_hash(request)
        
        self.engine.execute('DELETE FROM sessions WHERE hash = ? OR token = ?', browserHash, token)
        self.engine.execute('INSERT INTO sessions (hash, token, expire, username, password, engine, host, port) VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
                                browserHash,
                                token,
                                values['expire'],
                                values['username'],
                                aes256.encrypt(values['password'], browserHash + token),
                                values['engine'],
                                values['host'],
                                values['port']
                            )

        return Session(values)

    def clear(self, request):
        if 'token' in request.args:
            self.engine.execute('DELETE FROM sessions WHERE token = ? AND hash = ?', request.args['token'], self.__get_browser_hash(request))
        
        return None

session_store = SessionStore()

class Session(object):
    def __init__(self, row):
        self.expire = row['expire']
        try:
            self.engine = create_engine('%s://%s:%s@%s:%d' % (
                                row['engine'],
                                row['username'],
                                row['password'],
                                row['host'],
                                row['port'],
                            ))

            self.engine.connect()
        except OperationalError as e:
            self.engine = None
    
    def is_connected(self):
        return self.engine is not None

    @property
    def get_engine(self):
        return self.engine
    
    def get_expire(self):
        return self.expire