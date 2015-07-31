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
            <img class="media-object square-32" src="{{icon}}"/>
        </div>
        <div class="media-body">
        {% if archived %}
            This hub has been archived and locked.
        {% else %}
            Cobweb alert!  This hub was last active {{then}}.
        {% endif %}
        </div>
    </li>
</ul>
{% endif %}
""")


def data(session, widget):
    days = widget.hub.days_idle
    archived = widget.hub.archived
    old = days > 31 or archived
    then = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    then = arrow.get(then).humanize()
    import flask
    if archived:
        icon = flask.url_for('static', filename='img/archived.png')
    else:
        icon = flask.url_for('static', filename='img/cobweb.png')
    return dict(old=old, days=days, then=then, icon=icon, archived=archived)


#@hint(topics=[_('hubs.widget.update')])
def should_invalidate(message, session, widget):
    raise NotImplementedError()
