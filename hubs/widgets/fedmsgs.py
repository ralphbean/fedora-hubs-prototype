from hubs.widgets.base import argument

import jinja2


import hubs.validators as validators


template = jinja2.Template("""
<div class="flex-container">

    <img src="{{url}}" />

</div>
""")

from hubs.widgets.chrome import panel
chrome = panel("Daily Activity")


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):
    url = "https://apps.fedoraproject.org/datagrepper/charts/line?delta=86400&N=12&style=clean&height=200&fill=true&user={username}"
    url = url.format(username=username)
    return dict(url=url)


def should_invalidate(message, session, widget):
    raise NotImplementedError
