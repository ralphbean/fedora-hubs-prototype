#!/usr/bin/env python
""" Populate the hubs db with some dev data. """

import json

import hubs.models

import fedmsg.config
fedmsg_config = fedmsg.config.load_config()

session = hubs.models.init(fedmsg_config['hubs.sqlalchemy.uri'], True, True)

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

session.commit()

