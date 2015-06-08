import collections
import decorator

import fedmsg.config

import logging
log = logging.getLogger('hubs.hinting')


def hint(topics=None, categories=None, usernames=None):
    topics = topics or []
    categories = categories or []
    usernames = usernames or lambda x: []

    @decorator.decorator
    def wrapper(fn, *args, **kwargs):
        return fn(*args, **kwargs)

    def wrapper_wrapper(fn):
        wrapped = wrapper(fn)
        wrapped.hints = dict(
            topics=topics,
            categories=categories,
            username_function=usernames,
        )
        return wrapped

    return wrapper_wrapper


def prefixed(topic, prefix='org.fedoraproject'):
    config = fedmsg.config.load_config()  # This is memoized for us.
    return '.'.join([prefix, config['environment'], topic])
