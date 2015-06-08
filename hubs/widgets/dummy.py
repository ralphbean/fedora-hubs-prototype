from hubs.hinting import hint, prefixed as _
from hubs.widgets.chrome import panel
from hubs.widgets.base import argument

import jinja2

import hubs.validators as validators


template = jinja2.Template("{{text}}")
chrome = panel("This is a dummy widget")

@argument(name="text", default="Lorem ipsum dolor...",
          validator=validators.text,
          help="Some dummy text to display.")
def data(session, widget, text):
    return dict(text=text)


@hint(topics=[_('hubs.widget.update')])
def should_invalidate(message, session, widget):
    if not message['topic'].endswith('hubs.widget.update'):
        return False
    if message['msg']['widget']['id'] != widget.id:
        return False
    return True
