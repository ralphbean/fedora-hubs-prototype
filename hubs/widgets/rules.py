from collections import OrderedDict as ordereddict

import jinja2

from hubs.hinting import hint, prefixed as _
from hubs.widgets.chrome import panel
from hubs.widgets.base import argument, avatar
from hubs import validators

chrome = panel()
template = jinja2.Template("""
<div class="rules-container">
  {% if link %}
  <p class="small-heading">community rules</p>
  <p><a href="{{link}}">Community Rules and Guidelines</a></p>
  {% endif %}
  <p class="small-heading">group owners</p>
  {% for owner in owners %}
    <span><img class="img-circle" src="{{owners[owner]}}"/> {{owner}}</span>
  {% endfor %}
</div>
<style>
  .rules-table {
    width: 180px
    padding: 0px;
    margin: 0px;
    display: inline-block;
  }
  .small-heading {
    text-transform: uppercase;
    font-size: 80%;
    color: #797a7c;
  }
  .rules-table td {
    font-size: 32pt;
  }
</style>
""")

@argument(name='link', default=None,
          validator=validators.link,
          help="Link to the community rules and guidelines")
def data(session, widget, link):
    owners = widget.hub.owners
    owners = ordereddict([(o, avatar(o)) for o in owners])
    return dict(owners=owners, link=link)


@hint(topics=[_('hubs.widget.update'), _('hubs.hub.update')])
def should_invalidate(message, session, widget):
    if message['topic'].endswith('hubs.widget.update'):
        if message['msg']['widget']['id'] == widget.id:
            return True

    if message['topic'].endswith('hubs.hub.update'):
        if message['msg']['hub']['name'] == widget.hub.name:
            return True

    return False
