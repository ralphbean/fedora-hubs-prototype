import collections
import functools
import hashlib
import urllib

Argument = collections.namedtuple('Argument', ('name', 'default', 'validator', 'help'))


def argument(name, default, validator, help):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        inner.widget_arguments.append(Argument(name, default, validator, help))
        return inner
    return decorator

def wraps(original):
    @functools.wraps(original)
    def decorator(subsequent):
        subsequent = functools.wraps(original)(subsequent)
        subsequent.widget_arguments = getattr(original, 'widget_arguments', [])
        return subsequent
    return decorator


def avatar(username, size=32):
    openid = 'http://%s.id.fedoraproject.org/' % username
    query = urllib.urlencode({'s': size, 'd': 'retro'})
    hash = hashlib.sha256(openid).hexdigest()
    template = "https://seccdn.libravatar.org/avatar/%s?%s"
    return template % (hash, query)
