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
  <h6>community rules</h6>
  <p><a href="{{link}}">Community Rules and Guidelines</a></h6>
  {% endif %}
  <h6>group owners</h6>
  <div class="row">
    {% for owner in owners %}
        <div class="col-sm-6">
            <img class="img-circle" src="{{owners[owner]}}"/> {{owner}}
        </div>
    {% endfor %}
  </div>
  {% if schedule_text or schedule_link or minutes_link %}
  <h6>meetings</h6>
  {% if schedule_text %}
  <p>{{schedule_text}}</p>
  {% endif %}
  <p>
  {% if schedule_link %}
  <a target="_blank" href="{{schedule_link}}">Meeting Schedule</a>
  {% endif %}
  {% if schedule_link and minutes_link %}
  &#8214;
  {% endif %}
  {% if minutes_link %}
  <a target="_blank" href="{{minutes_link}}">Past Meeting Minutes</a>
  {% endif %}
  </p>
  {% endif %}
</div>
<style>
  .rules-table {
    width: 180px
    padding: 0px;
    margin: 0px;
    display: inline-block;
  }
  .rules-table td {
    font-size: 32pt;
  }
</style>
""")

@argument(name='link', default=None,
          validator=validators.link,
          help="Link to the community rules and guidelines")
@argument(name='schedule_text', default=None,
          validator=validators.text,
          help="Some text about when meetings are")
@argument(name='schedule_link', default=None,
          validator=validators.link,
          help="Link to a schedule for IRC meetings, etc..")
@argument(name='minutes_link', default=None,
          validator=validators.link,
          help="Link to meeting minutes from past meetings..")
def data(session, widget, link, schedule_text, schedule_link, minutes_link):
    owners = widget.hub.owners
    owners = ordereddict([(o.username, avatar(o.username)) for o in owners])
    return dict(owners=owners, link=link,
                schedule_text=schedule_text,
                schedule_link=schedule_link,
                minutes_link=minutes_link)


@hint(topics=[_('hubs.widget.update'), _('hubs.hub.update')])
def should_invalidate(message, session, widget):
    if message['topic'].endswith('hubs.widget.update'):
        if message['msg']['widget']['id'] == widget.id:
            return True

    if message['topic'].endswith('hubs.hub.update'):
        if message['msg']['hub']['name'] == widget.hub.name:
            return True

    return False
