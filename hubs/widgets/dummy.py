from chrome import panel
from base import argument

import hubs.validators as validators

@panel("This is a dummy widget")
@argument(name="text", default="Lorem ipsum dolor...",
          validator=validators.text,
          help="Some dummy text to display.")
def render(request, session, text):
    return text
