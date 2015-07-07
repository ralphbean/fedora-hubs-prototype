from hubs.hinting import hint, prefixed as _
from hubs.widgets.chrome import panel

import jinja2

chrome = panel()
template = jinja2.Template("""
<div class="stats-container">
  <table class="stats-table">
    <tr><th>Members</th><th>Subscribers</th></tr>
    <tr class="text-info"><td>{{members | length}}</td><td>{{subscribers | length}}</td></tr>
  </table>
  {% if g.auth.logged_in %}
    {% if g.auth.nickname in members %}
    <div class="pull-right"><button class="btn btn-danger">Resign</button></div>
    {% elif g.auth.nickname in subscribers %}
    <div class="pull-right"><button class="btn btn-warning">Unsubscribe</button></div>
    {% else %}
    <div class="pull-right"><button class="btn btn-info">Subscribe</button></div>
    {% endif %}
  {% else %}
    <div class="pull-right"><button class="btn btn-info">Subscribe</button></div>
  {% endif %}
</div>
""")


def data(session, widget):
    return dict(
        owners=[u.username for u in widget.hub.owners],
        members=[u.username for u in widget.hub.members],
        subscribers=[u.username for u in widget.hub.subscribers],
    )


@hint(topics=_('hubs.hub.update'))
def should_invalidate(message, session, widget):
    if message['topic'].endswith('hubs.hub.update'):
        if message['msg']['hub']['name'] == widget.hub.name:
            return True

    # TODO -- also check for FAS group changes??  are we doing that?

    return False
