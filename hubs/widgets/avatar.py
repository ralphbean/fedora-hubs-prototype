from hashlib import sha256

from hubs.widgets.base import argument

import jinja2

from six.moves.urllib_parse import urlencode

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

    query = urlencode({
        'd': 'retro',
        's': 312,
    })
    openid = 'http://%s.id.fedoraproject.org/' % username
    hash = sha256(openid.encode('utf-8')).hexdigest()
    avatar = "https://seccdn.libravatar.org/avatar/%s?%s" % (hash, query)

    return dict(username=username, avatar=avatar)


def should_invalidate(message, session, widget):
    raise NotImplementedError
