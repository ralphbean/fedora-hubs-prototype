import os

import flask

import models

app = flask.Flask(__name__)


# TODO - put this in config so we can migrate to pagure
# TODO - instead of 'develop', use the version from pkg_resources to figure out
#        the right tag to link people to.  AGPL ftw.
SOURCE_URL = 'https://github.com/ralphbean/fedora-hubs-prototype/blob/develop'


app.config.from_object('default_config')
if 'HUBS_CONFIG' in os.environ:
    app.config.from_envvar('HUBS_CONFIG')


@app.route('/')
def index():
    return flask.redirect('/designteam')  # TODO - remove this later


@app.route('/<name>')
@app.route('/<name>/')
def hub(name):
    session = models.init(app.config['DB_URL'])
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
def widget(hub, idx):
    session = models.init(app.config['DB_URL'])
    widget = get_widget(session, hub, idx)
    return widget.render(session, hub, idx)


@app.route('/<hub>/<idx>/source')
@app.route('/<hub>/<idx>/source/')
def widget_source(hub, idx):
    from hubs.widgets import registry
    base = '/hubs/'
    session = models.init(app.config['DB_URL'])
    widget = get_widget(session, hub, idx)
    fname = base + registry[widget.plugin].__file__.split(base, 1)[1][:-1]
    return flask.redirect(SOURCE_URL + fname)


if __name__ == '__main__':
    app.run(debug=True)
