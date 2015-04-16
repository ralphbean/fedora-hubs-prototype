from chrome import panel
from base import argument

import hubs.validators as validators

@panel(title='Sticky Note', klass="panel-info")
@argument(name="text", default="Lorem ipsum dolor...",
          validator=validators.text,
          help="Some dummy text to display.")
def render(request, session, widget, text):
    # TODO -- render with markdown
    return text
