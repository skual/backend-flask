# coding=utf-8

from utils import LazyView, Url

base_url = '/api/v1'

urls = (
    Url(base_url + '/connect', LazyView('views.authentication.connect'), 'POST'),
    Url(base_url + '/disconnect', LazyView('views.authentication.disconnect'), 'POST'),
    Url(base_url + '/test', LazyView('views.authentication.test')),
)