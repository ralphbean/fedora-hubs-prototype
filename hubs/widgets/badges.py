import requests

from hubs.widgets.base import argument

import jinja2


import hubs.validators as validators


template = jinja2.Template("""
{% for badge in assertions %}
    <img src="{{badge['image']}}"/>
{%endfor%}
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
    import pprint; pprint.pprint(response.json())

    return response.json()


def should_invalidate(message, session, widget):
    raise NotImplementedError
