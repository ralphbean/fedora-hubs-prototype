from __future__ import print_function

from hubs.hinting import hint
from hubs.widgets.base import argument

import fmn.lib
import fmn.lib.hinting

import datanommer.models

import arrow
import jinja2
import munch
import requests

import hubs.validators as validators

import datetime
import logging
log = logging.getLogger('hubs')

import fedmsg.config
config = fedmsg.config.load_config()
fmn_url = config['fmn.url']


bazillion = 1000
paths = fmn.lib.load_rules(root='fmn.rules')


template = jinja2.Template("""
{% for match in matches %}
<div class="panel panel-default">
  <div class="panel-body">
    <div class="media">
      <div class="media-left">
        <a href="{{match['link']}} target="_blank">
          <img class="media-object img-responsive square-32 img-circle" src="{{match['secondary_icon']}}">
        </a>
      </div>
      <div class="media-body">
        <h4 class="media-heading">{{match['subtitle']}}</h4>
        {{match['human_time']}}
      </div>
    </div>
  </div>
</div>
{% endfor %}
""")

# No chrome around the feed.
#from hubs.widgets.chrome import panel
#chrome = panel()


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
@argument(name="fmn_context",
          default="irc", # TODO - Make this 'hubs', or...
          validator=validators.fmn_context,
          help="A FMN context.")
def data(session, widget, username, fmn_context):
    openid = '%s.id.fedoraproject.org' % username
    url = '/'.join([fmn_url, 'api', openid, fmn_context])
    log.info("Getting FMN preferences from %s" % url)
    print(url)
    response = requests.get(url)
    preference = response.json()
    preference = rehydrate_preferences(preference)

    # The smaller we make this, the faster it is.
    delta = datetime.timedelta(days=365)
    end = datetime.datetime.utcnow()

    # We currently only support getting the first page.
    # The widget framework as currently written doesn't support
    # multiple pages yet.
    page = 1

    messages = []
    for filter in preference['filters']:
        rules = filter['rules']
        fmn_hinting = fmn.lib.hinting.gather_hinting(config, rules, paths)
        total, pages, rows = datanommer.models.Message.grep(
            start=end-delta,
            end=end,
            rows_per_page=bazillion,
            page=page,
            order='desc',
            **fmn_hinting
        )
        messages.extend(rows)

    matches = []
    for message in messages:
        original = message.__json__()
        recipients = fmn.lib.recipients(
            [preference], message.__json__(), paths, config)
        if recipients:
            matches.append(original)

    # TODO - sort messages and remove duplicates

    # Smash multiple messages into single ones
    matches = fedmsg.meta.conglomerate(matches, **config)

    return dict(
        matches=matches,
    )


@hint()
def should_invalidate(message, session, widget):
    # only if a new message would match the FMN filters would this be
    # invalidated... but that is as expensive as being FMN ourselves.
    raise NotImplementedError


def rehydrate_preferences(preference):
    for fltr in preference['filters']:
        fltr['rules'] = [munch.Munch(r) for r in fltr['rules']]
        for rule in fltr['rules']:
            code_path = str(rule.code_path)
            rule.fn = fedmsg.utils.load_class(code_path)

    return preference

def make_result(msg, d):
    return {
        'icon': fedmsg.meta.msg2icon(d, **config),
        'icon2': fedmsg.meta.msg2secondary_icon(d, **config),
        'subtitle': fedmsg.meta.msg2subtitle(d, **config),
        'link': fedmsg.meta.msg2link(d, **config),
        'time': arrow.get(msg.timestamp).humanize(),
    }
