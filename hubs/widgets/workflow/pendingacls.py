import requests

from hubs.hinting import hint, prefixed as _
from hubs.widgets.base import argument
from hubs.utils import username2avatar

import jinja2


import hubs.validators as validators

# TODO -- add approve/deny buttons or just link through to pkgdb
template = jinja2.Template("""
{% if pending_acls %}
{% if session['nickname'] == username %}
<a class="btn btn-success" target="_blank" href="https://admin.fedoraproject.org/pkgdb/acl/pending/">Manage requests</a>
<hr/>
{% endif %}
<ul class="media-list">
{% for acl in pending_acls %}
    <li class="media">
        <div class="media-left">
            <img class="media-object img-responsive img-circle" src="{{acl['avatar']}}"/>
        </div>
        <div class="media-body">
            <h4 class="media-heading">{{acl['user']}} is {{acl['status']}}</h4>
            for {{acl['acl']}} on
            {{acl['package']}}({{acl['collection']}})
        </div>
    </li>
{% endfor %}
</ul>
{% endif %}
""")

from hubs.widgets.chrome import panel
# If 'pending_acls' is empty, then don't render any chrome.
chrome = panel('Pending ACL Requests', key='pending_acls')


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):

    # TODO -- rewrite this to
    # 1) use the datagrepper API instead of the direct pkgdb API
    # 2) so that we can use the fedmsg.meta.conglomerate API to
    # 3) group messages nicely in the UI instead of having repeats
    # It will be slower, but that's fine because of our smart cache.

    baseurl = "https://admin.fedoraproject.org/pkgdb/api/pendingacls"
    query = "?username={username}&format=json".format(username=username)
    url = baseurl + query
    response = requests.get(url)
    data = response.json()
    for acl in data['pending_acls']:
        acl['avatar'] = username2avatar(acl['user'], s=32)
    data['username'] = username
    return data


@hint(topics=[_('pkgdb.acl.update')])
def should_invalidate(message, session, widget):
    # Search the message to see if I am in the ACLs list of the request.
    username = widget.config['username']

    for acl in message['msg']['package_listing']['acls']:
        if acl['fas_name'] == username and acl['status'] == 'Approved':
            return True

    return False
