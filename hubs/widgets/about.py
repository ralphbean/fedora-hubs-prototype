from hubs.hinting import hint, prefixed as _
from hubs.widgets.chrome import panel
from hubs.widgets.base import argument

import jinja2

import hubs.validators as validators


template = jinja2.Template("""
    <p>{{text}}</p>
    """)
chrome = panel("<span class='glyphicon glyphicon-info-sign' aria-hidden='true'></span> About")


@argument(name="text", default="I am a Fedora user, and this is my about",
          validator=validators.text,
          help="Text about a user.")
def data(session, widget, text):
    return dict(text=text)


@hint(topics=[_('hubs.widget.update')])
def should_invalidate(message, session, widget):
    if not message['topic'].endswith('hubs.widget.update'):
        return False
    if message['msg']['widget']['id'] != widget.id:
        return False
    return True
