from hubs.hinting import hint
from hubs.widgets.base import argument

import jinja2

import hubs.validators as validators

import fedmsg.config
config = fedmsg.config.load_config()


template = jinja2.Template("""
<div class="flex-container">

    <img src="{{url}}" />

</div>
""")

from hubs.widgets.chrome import panel
chrome = panel("Weekly Activity")


@argument(name="username",
          default=None,
          validator=validators.username,
          help="A FAS username.")
def data(session, widget, username):
    categories = ['git', 'Wiki', 'Copr', 'anitya', 'mirrormanager', 'ansible',
                  'fedoratagger', 'Pkgdb', 'summershum', 'nuancier', 'Mailman',
                  'fedbadges', 'FMN', 'koschei', 'compose', 'fedimg',
                  'Jenkins', 'irc', 'FAS', 'buildsys', 'Askbot', 'pagure',
                  'Bodhi', 'faf', 'kerneltest', 'github', 'Trac', 'meetbot',
                  'planet', 'fedocal', 'hotness']
    categories = [c.lower() for c in categories]
    categories = "&".join(['category=%s' % c for c in categories ])
    url = "https://apps.fedoraproject.org/datagrepper/charts/stackedline?delta=604800&N=12&style=clean&height=300&fill=true&user={username}&split_on=categories"
    url = url + "&" + categories
    url = url.format(username=username)
    return dict(url=url)


@hint(usernames=lambda widget: [widget.config['username']])
def should_invalidate(message, session, widget):
    usernames = fedmsg.meta.msg2usernames(message, **config)
    username = widget.config['username']
    return username in usernames
