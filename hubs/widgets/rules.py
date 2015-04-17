from collections import OrderedDict as ordereddict

import jinja2

from hubs.widgets.chrome import panel
from hubs.widgets.base import argument, avatar
from hubs import validators

rules_template = jinja2.Template("""
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

@panel()
@argument(name='link', default=None,
          validator=validators.link,
          help="Link to the community rules and guidelines")
def render(request, session, widget, link):
    owners = widget.hub.owners
    owners = ordereddict([(o, avatar(o)) for o in owners])
    return rules_template.render(owners=owners, link=link)
