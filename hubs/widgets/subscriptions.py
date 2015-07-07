#from hubs.hinting import hint, prefixed as _
from hubs.widgets.base import argument
from hubs.widgets.chrome import panel

from hubs import validators

import hubs.models

from fedmsg.meta.base import BaseConglomerator as BC

import jinja2

chrome = panel('Hubs', key='associations')
template = jinja2.Template("""
{% if associations %}
    {% if memberships %}
        <p>Belongs to: {{memberships_text}}</p>
    {% endif %}
    <hr/>
    {% if subscriptions %}
        <p>Subscribes to: {{subscriptions_text}}</p>
    {% endif %}
{% endif %}
""")


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):
    user = hubs.models.User.by_username(session, username)
    ownerships = [u.name for u in user.ownerships]
    memberships = [u.name for u in user.memberships]
    subscriptions = [u.name for u in user.subscriptions]
    return dict(
        associations=memberships + ownerships,
        ownerships=ownerships,
        memberships=memberships,
        subscriptions=subscriptions,
        ownerships_text=BC.list_to_series(ownerships),
        memberships_text=BC.list_to_series(memberships),
        subscriptions_text=BC.list_to_series(subscriptions),
    )


def should_invalidate(message, session, widget):
    raise NotImplementedError()
