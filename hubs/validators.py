import kitchen.text.converters


def text(value):
    return kitchen.text.converters.to_unicode(value)

def link(value):
    # TODO -- verify that this is actually a link
    return value
