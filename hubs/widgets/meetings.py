#from hubs.hinting import hint, prefixed as _
from hubs.widgets.base import argument
from hubs.widgets.chrome import panel

from hubs import validators

import arrow
import collections
import datetime
import jinja2
import requests

chrome = panel('Reminders', key='meetings')

def next_meeting(meetings):
    now = datetime.datetime.utcnow()
    for meeting in meetings:
        string = "%s %s" % (meeting['meeting_date'],
                            meeting['meeting_time_start'])
        dt = datetime.datetime.strptime(string, "%Y-%m-%d %H:%M:%S")

        if now < dt:
            meeting['human_time'] = arrow.get(dt).humanize()
            meeting['start_date'] = dt.strftime('%b %d')
            # Just UTC for now until we do this on the client and can access
            # their local with moment.js.
            meeting['start_time'] = meeting['meeting_time_start'][:-3] + " UTC"
            meeting['location'] = meeting['meeting_location']
            if '@' in meeting['location']:
                meeting['location'] = '#' + meeting['location'].split('@')[0]
            return meeting

    return None

jinja2_environment = jinja2.Environment()
jinja2_environment.filters['next_meeting'] = next_meeting
template = jinja2_environment.from_string("""
{% if meetings %}
    {% for title, items in meetings.items() %}
        {% set next = items | next_meeting %}
        {% if next %}
        The {{ next.meeting_name }} is {{ next.human_time }}
        <h1 class='inline'>{{next.start_date}}</h1>
        <div class='inline'>
            @{{next.start_time}}<br/>
            {{next.location}}
        </div>
        {% endif %}
        {% if meetings | length > 1 %}
        <hr/>
        {% endif %}
    {% endfor %}
{% endif %}
""")


@argument(name="calendar",
          default=None,
          validator=validators.required,
          help="A fedocal calendar.")
def data(session, widget, calendar):
    base = 'https://apps.fedoraproject.org/calendar/api/meetings/?calendar=%s'
    url = base % calendar
    response = requests.get(url).json()

    meetings = collections.defaultdict(list)
    for meeting in response['meetings']:
        meetings[meeting['meeting_name']].append(meeting)

    return dict(meetings=dict(meetings))


def should_invalidate(message, session, widget):
    raise NotImplementedError()
