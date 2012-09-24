# coding=utf-8

from werkzeug import import_string, cached_property

class LazyView(object):

    def __init__(self, import_name):
        self.__module__, self.__name__ = import_name.rsplit('.', 1)
        self.import_name = import_name

    @cached_property
    def view(self):
        return import_string(self.import_name)

    def __call__(self, *args, **kwargs):
        return self.view(*args, **kwargs)

class Url(object):
    """
    Act as a Url config object for each registered urls
    Makes the configuration easier to read
    """

    def __init__(self, path, view, *args, **kwargs):
        self._path = path
        self._options = kwargs
        self._options['view_func'] = view

        if len(args) > 0 and args[0] in ['GET', 'POST', 'PUT', 'DELETE', 'HEAD']:
            self._options['methods'] = args

        if not 'methods' in self._options:
            self._options['methods'] = ['GET',]

    @property
    def path(self):
        return self._path

    @property
    def options(self):
        return self._options
