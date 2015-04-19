#!/usr/bin/env python
""" Populate the hubs db with some dev data. """

import json
import os

import flask

import hubs.models

app = flask.Flask(__name__)
app.config.from_object('hubs.default_config')
if 'HUBS_CONFIG' in os.environ:
    app.config.from_envvar('HUBS_CONFIG')

session = hubs.models.init(app.config['DB_URL'], True, True)

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
widget = hubs.models.Widget(plugin='sticky', index=0, left=True,
                            _config=json.dumps({
                                'text': 'This is a sticky note.',
                            }))
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='dummy', index=1, left=True)
hub.widgets.append(widget)

session.commit()

