from hubs.hinting import hint, prefixed as _
from hubs.widgets.chrome import panel

import flask
import jinja2

chrome = panel()
template = jinja2.Template("""
<div class="stats-container">
  <table class="stats-table">
    <tr><th>Members</th><th>Subscribers</th></tr>
    <tr class="text-info"><td>{{members | length}}</td><td>{{subscribers | length}}</td></tr>
  </table>

  {% if g.auth.logged_in %}
    <div class="pull-right">
    {% if g.auth.nickname in members %}
    <form action="{{hub_leave_url}}" method="POST">
        <button class="btn btn-danger">Leave Hub</button>
    </form>
    {% elif g.auth.nickname in subscribers %}
    <form action="{{hub_unsubscribe_url}}" method="POST">
        <button class="btn btn-warning">Unsubscribe</button>
    </form>
    {% else %}
    <form action="{{hub_subscribe_url}}" method="POST">
        <button class="btn btn-info">Subscribe</button>
    </form>
    {% endif %}
    </div>
  {% else %}
    <div class="pull-right">
        <form action="{{hub_subscribe_url}}" method="POST">
            <button class="btn btn-info">Subscribe</button>
        </form>
    </div>
  {% endif %}
</div>
""")


def data(session, widget):
    return dict(
        owners=[u.username for u in widget.hub.owners],
        members=[u.username for u in widget.hub.members],
        subscribers=[u.username for u in widget.hub.subscribers],
        hub_leave_url=flask.url_for('hub_leave', hub=widget.hub.name),
        hub_join_url=flask.url_for('hub_join', hub=widget.hub.name),
        hub_subscribe_url=flask.url_for('hub_subscribe', hub=widget.hub.name),
        hub_unsubscribe_url=flask.url_for('hub_unsubscribe', hub=widget.hub.name),
    )


@hint(topics=_('hubs.hub.update'))
def should_invalidate(message, session, widget):
    if message['topic'].endswith('hubs.hub.update'):
        if message['msg']['hub']['name'] == widget.hub.name:
            return True

    # TODO -- also check for FAS group changes??  are we doing that?

    return False
