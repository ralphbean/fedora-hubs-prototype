import json

import hubs.models


def add_user_widgets(session, hub, username, fullname):
    """ Some defaults for an individual user's hub. """
    widget = hubs.models.Widget(
        plugin='sticky', index=0, left=True,
        _config=json.dumps({
            'text': 'TODO -- put a fancy graph here..',
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='avatar', index=0,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='workflow.pendingacls', index=1,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='badges', index=2,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    return hub
