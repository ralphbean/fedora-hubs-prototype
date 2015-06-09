import json

import hubs.models


def add_user_widgets(session, hub, username, fullname):
    """ Some defaults for an individual user's hub. """
    widget = hubs.models.Widget(
        plugin='fedmsgs', index=0, left=True,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='feed', index=1, left=True,
        _config=json.dumps({
            'username': username,
            'fmn_context': 'irc',  # TODO -- make this 'hubs'
        }))
    hub.widgets.append(widget)

    # Right Side Widgets
    widget = hubs.models.Widget(
        plugin='avatar', index=0,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='fedmsgstats', index=1,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='workflow.updates2stable', index=2,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='workflow.pendingacls', index=3,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    widget = hubs.models.Widget(
        plugin='badges', index=4,
        _config=json.dumps({
            'username': username,
        }))
    hub.widgets.append(widget)
    return hub
