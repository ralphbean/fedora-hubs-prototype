import os

import flask

import models

app = flask.Flask(__name__)


# TODO - put this in config so we can migrate to pagure
# TODO - instead of 'develop', use the version from pkg_resources to figure out
#        the right tag to link people to.  AGPL ftw.
SOURCE_URL = 'https://github.com/ralphbean/fedora-hubs-prototype/blob/develop'


app.config.from_object('hubs.default_config')
if 'HUBS_CONFIG' in os.environ:
    app.config.from_envvar('HUBS_CONFIG')

import fedmsg.config
fedmsg_config = fedmsg.config.load_config()


@app.route('/')
def index():
    return flask.redirect('/designteam')  # TODO - remove this later


@app.route('/<name>')
@app.route('/<name>/')
def hub(name):
    session = models.init(fedmsg_config['hubs.sqlalchemy.uri'])
    hub = session.query(models.Hub)\
        .filter(models.Hub.name==name)\
        .first()

    if not hub:
        flask.abort(404)

    return flask.render_template('hubs.html', hub=hub, session=session)


def get_widget(session, hub, idx):
    try:
        idx = int(idx)
    except TypeError:
        flask.abort(404)

    hub = session.query(models.Hub)\
        .filter(models.Hub.name==hub)\
        .first()

    if not hub:
        flask.abort(404)

    for widget in hub.widgets:
        if widget.idx == idx:
            return widget

    flask.abort(404)


@app.route('/<hub>/<idx>')
@app.route('/<hub>/<idx>/')
def widget_render(hub, idx):
    session = models.init(fedmsg_config['hubs.sqlalchemy.uri'])
    widget = get_widget(session, hub, idx)

    # Make this artificially slow for development...
    import random, time
    s = (random.random() * 3) + 1
    print(widget.plugin, "sleeping artificially for", s)
    time.sleep(s)

    return widget.render(session)


@app.route('/<hub>/<idx>/json')
@app.route('/<hub>/<idx>/json/')
def widget_json(hub, idx):
    session = models.init(fedmsg_config['hubs.sqlalchemy.uri'])
    widget = get_widget(session, hub, idx)
    from hubs.widgets import registry
    module = registry[widget.plugin]
    data = module.data(session, widget, **widget.config)
    response = flask.jsonify(data)

    # We don't actually need these two headers.  Just messing around.
    response.headers['X-fedora-hubs-hub-name'] = hub
    response.headers['X-fedora-hubs-widget-id'] = idx
    # TODO -- add other headers here as we decide we need them.

    return response


@app.route('/source/<name>')
@app.route('/source/<name>/')
def widget_source(name):
    from hubs.widgets import registry
    base = '/hubs/'
    fname = base + registry[name].__file__.split(base, 1)[1][:-1]
    return flask.redirect(SOURCE_URL + fname)


if __name__ == '__main__':
    app.run(debug=True)
