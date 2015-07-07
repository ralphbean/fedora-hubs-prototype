#!/usr/bin/env python
""" Populate the hubs db with some dev data. """

import json

import hubs.models

import fedmsg.config
fedmsg_config = fedmsg.config.load_config()

session = hubs.models.init(fedmsg_config['hubs.sqlalchemy.uri'], True, True)

users = ['mrichard', 'duffy', 'ryanlerch', 'gnokii', 'nask0',
         'abompard', 'decause', 'ralph']
for username in users:
    fullname = 'Full Name Goes Here'
    openid = '%s.id.fedoraproject.org' % username
    print("Creating account for %r" % openid)
    hubs.models.User.get_or_create(
        session, openid=openid, fullname=fullname)

session.commit()


############## Infra team
hub = hubs.models.Hub(name='designteam', summary='The Fedora Design Team')
session.add(hub)

widget = hubs.models.Widget(plugin='stats', index=0)
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='rules', index=1,
                            _config=json.dumps({
                                'link': 'http://threebean.org'
                            }))
hub.widgets.append(widget)

widget = hubs.models.Widget(plugin='dummy', index=2)
hub.widgets.append(widget)

# Added a hubs about widget
widget = hubs.models.Widget(plugin='about', index=3,
                            _config=json.dumps({
                                "text": "I'm a Fedora user, and this is my about widget text!",
                            }))
hub.widgets.append(widget)

widget = hubs.models.Widget(plugin='sticky', index=0, left=True,
                            _config=json.dumps({
                                'text': 'This is a sticky note.',
                            }))
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='dummy', index=1, left=True)
hub.widgets.append(widget)


# Set up some memberships
hub.subscribe(session, hubs.models.User.by_openid(session, 'duffy.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'ryanlerch.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'gnokii.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'mrichard.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'nask0.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'decause.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'ralph.id.fedoraproject.org'), 'subscriber')


############## Infra team
hub = hubs.models.Hub(name='infrastructure', summary='The Fedora Infrastructure Team')
session.add(hub)

widget = hubs.models.Widget(plugin='stats', index=0)
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='rules', index=1,
                            _config=json.dumps({
                                'link': 'http://threebean.org'
                            }))
hub.widgets.append(widget)

widget = hubs.models.Widget(plugin='dummy', index=2)
hub.widgets.append(widget)

# Added a hubs about widget
widget = hubs.models.Widget(plugin='about', index=3,
                            _config=json.dumps({
                                "text": "I'm a Fedora user, and this is my about widget text!",
                            }))
hub.widgets.append(widget)

widget = hubs.models.Widget(plugin='sticky', index=0, left=True,
                            _config=json.dumps({
                                'text': 'This is a sticky note.',
                            }))
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='dummy', index=1, left=True)
hub.widgets.append(widget)


hub.subscribe(session, hubs.models.User.by_openid(session, 'ralph.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'abompard.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'nask0.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'decause.id.fedoraproject.org'), 'subscriber')

session.commit()
