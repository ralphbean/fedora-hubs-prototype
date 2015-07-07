import operator

import requests

from hubs.hinting import hint, prefixed as _
from hubs.widgets.base import argument

import jinja2


import hubs.validators as validators


template = jinja2.Template("""
<div class="flex-container">
{% for badge in assertions[:10] %}
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
    assertions = response.json()['assertions']
    key = operator.itemgetter('issued')
    return dict(assertions=sorted(assertions, key=key, reverse=True))


@hint(topics=[_('hubs.widget.update'), _('fedbadges.badge.award')])
def should_invalidate(message, session, widget):
    if message['topic'].endswith('hubs.widget.update'):
        if message['msg']['widget']['id'] != widget.id:
            return True

    if message['topic'].endswith('fedbadges.badge.award'):
        username = widget.config['username']
        if message['msg']['user']['username'] == username:
            return True

    return False
