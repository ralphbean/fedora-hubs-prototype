from hubs.hinting import hint, prefixed as _
from hubs.widgets.chrome import panel

from hubs.utils import commas

import flask
import jinja2

chrome = panel()
template = jinja2.Template("""
<div class="stats-container row">
<div class="col-md-7">
  <table class="stats-table">
    <tr><th>Members</th><th>Subscribers</th></tr>
    <tr class="text-info"><td>{{members_text}}</td><td class="text-right">{{subscribers_text}}</td></tr>
  </table>
</div>
<div class="col-md-5">
  <ul class="list-unstyled">
  {% if g.auth.nickname in subscribers %}
  <li><form action="{{hub_unsubscribe_url}}" method="POST">
      <button class="btn btn-info"><span class="glyphicon glyphicon-remove-sign" aria-hidden="true"></span> Unsubscribe</button>
  </form></li>
  {% else %}
  <li><form action="{{hub_subscribe_url}}" method="POST">
      <button class="btn btn-default"><span class="glyphicon glyphicon-plus" aria-hidden="true"></span> Subscribe</button>
  </form></li>
  {% endif %}

  {% if g.auth.nickname in stargazers %}
  <li><form action="{{hub_unstar_url}}" method="POST">
      <button class="btn btn-info"><span class="glyphicon glyphicon-remove-sign" aria-hidden="true"></span> Unstar Hub</button>
  </form></li>
  {% else %}
  <li><form action="{{hub_star_url}}" method="POST">
      <button class="btn btn-default"><span class="glyphicon glyphicon-star" aria-hidden="true"></span> Star Hub</button>
  </form></li>
  {% endif %}

  {% if g.auth.nickname in members %}
  <li><form action="{{hub_leave_url}}" method="POST">
      <button class="btn btn-info"><span class="glyphicon glyphicon-remove-sign" aria-hidden="true"></span> Leave Hub</button>
  </form></li>
  {% else %}
  <li><form action="{{hub_join_url}}" method="POST">
      <button class="btn btn-default"><span class="glyphicon glyphicon-user" aria-hidden="true"></span> Join Hub</button>
  </form></li>
  {% endif %}
  </ul>
</div>
</div>
""")


def data(session, widget):
    owners = [u.username for u in widget.hub.owners]
    members = [u.username for u in widget.hub.members]
    subscribers = [u.username for u in widget.hub.subscribers]
    stargazers = [u.username for u in widget.hub.stargazers]

    return dict(
        owners=owners,
        members=members,
        subscribers=subscribers,
        stargazers=stargazers,

        owners_text=commas(len(owners)),
        members_text=commas(len(members)),
        subscribers_text=commas(len(subscribers)),
        stargazers_text=commas(len(stargazers)),

        hub_leave_url=flask.url_for('hub_leave', hub=widget.hub.name),
        hub_join_url=flask.url_for('hub_join', hub=widget.hub.name),
        hub_unstar_url=flask.url_for('hub_unstar', hub=widget.hub.name),
        hub_star_url=flask.url_for('hub_star', hub=widget.hub.name),
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
