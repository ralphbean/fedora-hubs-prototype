import requests

from hubs.widgets.base import argument
from hubs.utils import username2avatar

import jinja2


import hubs.validators as validators

# TODO -- add approve/deny buttons or just link through to pkgdb
template = jinja2.Template("""
{% if pending_acls %}
<a class="btn btn-success" target="_blank" href="https://admin.fedoraproject.org/pkgdb/acl/pending/">Manage requests</a>
<hr/>
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
chrome = panel("Pending ACLs")


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):
    baseurl = "https://admin.fedoraproject.org/pkgdb/api/pendingacls"
    query = "?username={username}&format=json".format(username=username)
    url = baseurl + query
    response = requests.get(url)
    data = response.json()
    for acl in data['pending_acls']:
        acl['avatar'] = username2avatar(acl['user'], s=32)
    return data


def should_invalidate(message, session, widget):
    raise NotImplementedError
