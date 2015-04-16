import collections
import functools


Argument = collections.namedtuple('Argument', ('name', 'default', 'help'))


def argument(name, default, help):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        inner.widget_arguments.append(Argument(name, default, help))
        return inner
    return decorator

def wraps(original):
    @functools.wraps(original)
    def decorator(subsequent):
        subsequent = functools.wraps(original)(subsequent)
        subsequent.widget_arguments = getattr(original, 'widget_arguments', [])
        return subsequent
    return decorator
