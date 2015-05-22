from hubs.widgets.chrome import panel
from hubs.widgets.base import argument

import jinja2

import hubs.validators as validators

template = jinja2.Template("{{text}}")

chrome = panel(title='Sticky Note', klass="panel-info")

@argument(name="text", default="Lorem ipsum dolor...",
          validator=validators.text,
          help="Some dummy text to display.")
def data(request, session, widget, text):
    # TODO -- render with markdown
    return dict(text=text)
