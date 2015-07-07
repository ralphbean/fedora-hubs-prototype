#!/usr/bin/env python
""" Populate the hubs db with some dev data. """

import json

import hubs.models

import fedmsg.config
fedmsg_config = fedmsg.config.load_config()

session = hubs.models.init(fedmsg_config['hubs.sqlalchemy.uri'], True, True)

users = ['mrichard', 'duffy', 'ryanlerch', 'gnokii', 'nask0',
         'abompard', 'decause', 'ralph', 'lmacken', 'croberts', 'mattdm']
for username in users:
    fullname = 'Full Name Goes Here'
    openid = '%s.id.fedoraproject.org' % username
    print("Creating account for %r" % openid)
    hubs.models.User.get_or_create(
        session, openid=openid, fullname=fullname)

session.commit()

############## Marketing team
hub = hubs.models.Hub(name='marketingteam', summary='The Fedora Marketing Team')
session.add(hub)

widget = hubs.models.Widget(plugin='stats', index=0)
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='rules', index=1,
                            _config=json.dumps({
                                'link': 'https://fedoraproject.org/wiki/Marketing'
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
                                'text': "The Fedora Marketing Team develops and executes marketing strategies to promote the usage and support of Fedora worldwide. Through the development of processes and content, this project aims to support the efforts of other Fedora projects to spread Fedora and to provide a central repository of ideas and information that can be used to deliver Fedora to new audiences. We work closely with the Fedora Ambassadors who spread the word about Fedora at events and allow the Fedora Project to interact directly with its existing and prospective users. ",
                            }))
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='dummy', index=1, left=True)
hub.widgets.append(widget)


# Set up some memberships
hub.subscribe(session, hubs.models.User.by_openid(session, 'croberts.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'ryanlerch.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'mrichard.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'mattdm.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'decause.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'ralph.id.fedoraproject.org'), 'subscriber')


session.commit()

############## Design team
hub = hubs.models.Hub(name='designteam', summary='The Fedora Design Team')
session.add(hub)

widget = hubs.models.Widget(plugin='stats', index=0)
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='rules', index=1,
                            _config=json.dumps({
                                'link': 'https://fedoraproject.org/wiki/Design'
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
                                'text': "The Design Team is the design group of the Fedora project. Our interests are not only in creating graphics for use by the Fedora community, but also in advocating the use of the creative tools that are a part of Fedora.",
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

session.commit()


############## Infra team
hub = hubs.models.Hub(name='infrastructure', summary='The Fedora Infrastructure Team')
session.add(hub)

widget = hubs.models.Widget(plugin='stats', index=0)
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='rules', index=1,
                            _config=json.dumps({
                                'link': 'https://fedoraproject.org/wiki/Infrastructure'
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
                                'text': "The Infrastructure Team consists of dedicated volunteers and professionals managing the servers, building the tools and utilities, and creating new applications to make Fedora development a smoother process. We're located all over the globe and communicate primarily by IRC and e-mail. ",
                            }))
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='dummy', index=1, left=True)
hub.widgets.append(widget)


hub.subscribe(session, hubs.models.User.by_openid(session, 'ralph.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'abompard.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'lmacken.id.fedoraproject.org'), 'owner')
hub.subscribe(session, hubs.models.User.by_openid(session, 'nask0.id.fedoraproject.org'), 'member')
hub.subscribe(session, hubs.models.User.by_openid(session, 'decause.id.fedoraproject.org'), 'subscriber')

session.commit()
