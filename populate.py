import os

import flask

import hubs.models

app = flask.Flask(__name__)
app.config.from_object('hubs.default_config')
if 'HUBS_CONFIG' in os.environ:
    app.config.from_envvar('HUBS_CONFIG')

session = hubs.models.init(app.config['DB_URL'], True, True)

hub = hubs.models.Hub(name='lol')
session.add(hub)

widget = hubs.models.Widget(plugin='dummy', index=0)
session.add(hub)
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='dummy', index=1)
session.add(hub)
hub.widgets.append(widget)
widget = hubs.models.Widget(plugin='dummy', index=0, left=True)
session.add(hub)
hub.widgets.append(widget)

session.commit()

