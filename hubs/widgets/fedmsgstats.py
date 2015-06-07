from hubs.widgets.chrome import panel

import jinja2

import requests

chrome = panel()
template = jinja2.Template("""
<div class="stats-container">
  <table class="stats-table">
    <tr><th>FedMsgs</th><th>Subscribers</th></tr>
    <tr class="text-info"><td>{{fedmsgs}}</td><td>{{subscribers}}</td></tr>
  </table>
  <div class="pull-right"><button class="btn btn-info">Subscribe</button></div>
</div>
""")


def data(session, widget, username):
    url = "https://apps.fedoraproject.org/datagrepper/raw?user={username}"
    url = url.format(username=username)
    response = requests.get(url)
    fedmsgs = response.json()['total']
    return dict(
        fedmsgs=fedmsgs,
        subscribers=len(widget.hub.subscribers),
    )


# TODO -- add topic-based hinting here.  Solved.
def should_invalidate(message, session, widget):
    if message['topic'].endswith('hubs.hub.update'):
        if message['msg']['hub']['name'] == widget.hub.name:
            return True

    # TODO -- also check for FAS group changes??  are we doing that?

    return False
