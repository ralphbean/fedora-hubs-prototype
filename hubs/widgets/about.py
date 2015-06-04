from hubs.widgets.chrome import panel
from hubs.widgets.base import argument

import jinja2

import hubs.validators as validators


template = jinja2.Template("""
    <p>{{text}}</p>
    """)
chrome = panel("About")


@argument(name="text", default="I am a Fedora user, and this is my about",
          validator=validators.text,
          help="Text about a user.")
def data(session, widget, text):
    return dict(text=text)


def should_invalidate(message, session, widget):
    raise NotImplementedError
