import collections

Argument = collections.namedtuple('Argument', ('name', 'default', 'help'))


def argument(name, default, help):
    def decorator(func):
        def inner(*args, **kwargs):
            return func(*args, **kwargs)

        inner.widget_arguments = getattr(func, 'widget_arguments', [])
        inner.widget_arguments.append(Argument(name, default, help))
        return inner
    return decorator
