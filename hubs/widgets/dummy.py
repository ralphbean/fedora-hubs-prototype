from chrome import panel
from base import argument

@panel("This is a dummy widget")
@argument(name="text", default="Lorem ipsum dolor...",
          help="Some dummy text to display.")
def render(request, session, text):
    return text
