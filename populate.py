import hubs.models

session = hubs.models.init('sqlite:////var/tmp/hubs.db', True, True)

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

