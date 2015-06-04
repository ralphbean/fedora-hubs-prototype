import requests

from hubs.widgets.base import argument

import jinja2


import hubs.validators as validators


template = jinja2.Template("""
<div class="flex-container">
{% for badge in assertions %}
    <img width="19%" src="{{badge['image']}}"/>
{%endfor%}
</div>
""")

from hubs.widgets.chrome import panel
chrome = panel("Badges")


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):
    url = "https://badges.fedoraproject.org/user/{username}/json"
    url = url.format(username=username)
    response = requests.get(url)
    return response.json()


def should_invalidate(message, session, widget):
    raise NotImplementedError
