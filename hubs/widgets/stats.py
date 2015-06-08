from hubs.hinting import hint, prefixed as _
from hubs.widgets.chrome import panel

import jinja2

chrome = panel()
template = jinja2.Template("""
<div class="stats-container">
  <table class="stats-table">
    <tr><th>Members</th><th>Subscribers</th></tr>
    <tr class="text-info"><td>{{members}}</td><td>{{subscribers}}</td></tr>
  </table>
  <div class="pull-right"><button class="btn btn-info">Subscribe</button></div>
</div>
""")


def data(session, widget):
    return dict(
        members=len(widget.hub.members),
        subscribers=len(widget.hub.subscribers),
    )


@hint(topics=_('hubs.hub.update'))
def should_invalidate(message, session, widget):
    if message['topic'].endswith('hubs.hub.update'):
        if message['msg']['hub']['name'] == widget.hub.name:
            return True

    # TODO -- also check for FAS group changes??  are we doing that?

    return False
