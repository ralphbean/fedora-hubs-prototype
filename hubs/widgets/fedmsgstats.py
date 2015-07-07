from hubs.hinting import hint
from hubs.widgets.chrome import panel

from hubs.utils import commas

import jinja2
import requests

import fedmsg.config
import fedmsg.meta

config = fedmsg.config.load_config()

chrome = panel()
template = jinja2.Template("""
<div class="stats-container">
  <table class="stats-table">
    <tr><th>FedMsgs</th><th>Subscribers</th></tr>
    <tr class="text-info"><td>{{fedmsgs_text}}</td><td class="text-right">{{subscribers_text}}</td></tr>
  </table>
  {% if session['nickname'] != username %}
  <div class="pull-right"><button class="btn btn-info">Subscribe</button></div>
  {% endif %}
</div>
""")


def data(session, widget, username):
    url = "https://apps.fedoraproject.org/datagrepper/raw?user={username}"
    url = url.format(username=username)
    response = requests.get(url)
    fedmsgs = response.json()['total']
    return dict(
        username=username,
        fedmsgs=fedmsgs,
        subscribers=len(widget.hub.subscribers),
        fedmsgs_text=commas(fedmsgs),
        subscribers_text=commas(len(widget.hub.subscribers)),
    )


@hint(usernames=lambda widget: [widget.config['username']])
def should_invalidate(message, session, widget):
    usernames = fedmsg.meta.msg2usernames(message, **config)
    username = widget.config['username']
    return username in usernames
