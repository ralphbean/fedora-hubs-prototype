from hubs.hinting import hint, prefixed as _
from hubs.widgets.base import argument
from hubs.utils import username2avatar

import jinja2

import hubs.validators as validators


template = jinja2.Template("""
<img class="img-responsive img-circle center-block" src="{{avatar}}">
""")

#from hubs.widgets.chrome import panel
#chrome = panel("About")


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):
    avatar = username2avatar(username)
    return dict(username=username, avatar=avatar)


@hint(topics=[_('hubs.widget.update')])
def should_invalidate(message, session, widget):
    if not message['topic'].endswith('hubs.widget.update'):
        return False
    if message['msg']['widget']['id'] != widget.id:
        return False
    return True
