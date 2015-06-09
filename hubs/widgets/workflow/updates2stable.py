import requests

from hubs.hinting import hint, prefixed as _
from hubs.widgets.base import argument

import jinja2


import hubs.validators as validators

# TODO -- add approve/deny buttons or just link through to pkgdb
template = jinja2.Template("""
{% if updates %}
{% if session['nickname'] == username %}
<a class="btn btn-success" target="_blank" href="https://admin.fedoraproject.org/updates/mine">Manage updates</a>
<hr/>
{% endif %}
<ul class="media-list">
{% for update in updates %}
    <li class="media">
        <div class="media-left">
            <a href="{{update['link']}}" target="_blank">
                <img class="media-object img-responsive square-32" src="{{update['icon']}}"/>
            </a>
        </div>
        <div class="media-body">
            <h4 class="media-heading">{{update['title']}} (karma {{update['karma']}})</h4>
            ready for love
        </div>
    </li>
{% endfor %}
</ul>
{% endif %}
""")

from hubs.widgets.chrome import panel
# If 'updates' is empty, then don't render any chrome.
chrome = panel('Updates Ready for Stable', key='updates')


giveaway = 'can be pushed to stable now'


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):

    # First, get all of my updates currently in testing.
    bodhiurl = 'https://admin.fedoraproject.org/updates/'
    baseurl = bodhiurl + 'list'
    query = '?username={username}&status=testing'.format(username=username)
    url = baseurl + query
    headers = {'Accept': 'application/json'}
    response = requests.get(url, headers=headers)
    data = response.json()

    # Limit it this to only the updates that haven't already requested stable
    # but which can actually be pushed to stable now.
    data['updates'] = [
        update for update in data['updates']
        if update['request'] is None and
        any([giveaway in comment['text'] for comment in update['comments']])
    ]

    # Stuff some useful information in there.
    baseurl = 'https://apps.fedoraproject.org/packages/images/icons/'
    for update in data['updates']:
        package = update['builds'][0]['package']['name']
        update['icon'] = baseurl + package + '.png'
        update['link'] = bodhiurl + update['title']

    return data


@hint(topics=[_('bodhi.update.comment')])
def should_invalidate(message, session, widget):
    if giveaway in message['msg']['comment']['text']:
        username = widget.config['username']
        if username == message['msg']['comment']['update_submitter']:
            return True

    return False
