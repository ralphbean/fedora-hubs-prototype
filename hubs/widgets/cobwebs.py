from hubs.hinting import hint, prefixed as _

import arrow
import datetime
import jinja2

from hubs.widgets.chrome import panel
chrome = panel(None, key='old', klass='panel-info')

template = jinja2.Template("""
{% if old %}
<ul class="media-list">
    <li class="media">
        <div class="media-left">
            <img class="media-object square-32" src="http://placekitten.com/g/32/32"/>
        </div>
        <div class="media-body">
            Cobweb alert!  This hub was last active {{then}}.
        </div>
    </li>
</ul>
{% endif %}
""")


def data(session, widget):
    days = widget.hub.days_idle
    old = days > 31
    then = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    then = arrow.get(then).humanize()
    return dict(old=old, days=days, then=then)


#@hint(topics=[_('hubs.widget.update')])
def should_invalidate(message, session, widget):
    raise NotImplementedError()
