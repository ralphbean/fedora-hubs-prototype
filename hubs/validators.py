import kitchen.text.converters

import hubs.models


def text(session, value):
    return kitchen.text.converters.to_unicode(value)

def link(session, value):
    # TODO -- verify that this is actually a link
    return value

def username(session, value):
    openid = 'http://%s.id.fedoraproject.org/' % value
    return not hubs.models.User.by_openid(session, openid) is None
