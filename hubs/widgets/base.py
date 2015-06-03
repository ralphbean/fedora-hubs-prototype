import collections
import functools
import hashlib
import json

import dogpile.cache
import flask
import six.moves.urllib_parse

import fedmsg.config

config = fedmsg.config.load_config()
cache_defaults = {
    "backend": "dogpile.cache.dbm",
    "expiration_time": 1,  # Expire every 1 second, for development
    "arguments": {
        "filename": "/var/tmp/fedora-hubs-cache.db",
    },
}
cache = dogpile.cache.make_region()
cache.configure(**config.get('fedora-hubs.cache', cache_defaults))


Argument = collections.namedtuple(
    'Argument', ('name', 'default', 'validator', 'help'))


def argument(name, default, validator, help):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        inner.widget_arguments.append(Argument(name, default, validator, help))
        return inner
    return decorator


def AGPLv3(name):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            result = func(*args, **kwargs)
            result['source_url'] = flask.url_for('widget_source', name=name)
            return result

        return inner
    return decorator


def smartcache(module):
    def decorator(func):
        @wraps(func)
        def inner(session, widget, *args, **kwargs):
            key = cache_key_generator(module, args, kwargs)
            creator = lambda: func(session, widget, *args, **kwargs)
            return cache.get_or_create(key, creator)

        return inner
    return decorator


def cache_key_generator(module, args, kwargs):
    return "|".join([
        module.__name__,
        json.dumps(args),
        json.dumps(kwargs),
    ]).encode('utf-8')


def wraps(original):
    @functools.wraps(original)
    def decorator(subsequent):
        subsequent = functools.wraps(original)(subsequent)
        subsequent.widget_arguments = getattr(original, 'widget_arguments', [])
        return subsequent
    return decorator


def avatar(username, size=32):
    openid = 'http://%s.id.fedoraproject.org/' % username
    query = six.moves.urllib_parse.urlencode({'s': size, 'd': 'retro'})
    hash = hashlib.sha256(openid.encode('utf-8')).hexdigest()
    template = "https://seccdn.libravatar.org/avatar/%s?%s"
    return template % (hash, query)
