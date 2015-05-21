from chrome import panel
from base import argument

import jinja2

import hubs.validators as validators


template = jinja2.Template("{{text}}")
chrome = panel("This is a dummy widget")

@argument(name="text", default="Lorem ipsum dolor...",
          validator=validators.text,
          help="Some dummy text to display.")
def data(request, session, widget, text):
    return dict(text=text)
