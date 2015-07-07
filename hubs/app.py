import functools
import logging
import os

import flask
import flask.json
import munch
import six

from flask.ext.openid import OpenID

import hubs.models

import datanommer.models


app = flask.Flask(__name__)

logging.basicConfig()


# TODO - put this in config so we can migrate to pagure
# TODO - instead of 'develop', use the version from pkg_resources to figure out
#        the right tag to link people to.  AGPL ftw.
SOURCE_URL = 'https://pagure.io/fedora-hubs/blob/develop/f'#/hubs/widgets/badges.py'

app.config.from_object('hubs.default_config')
if 'HUBS_CONFIG' in os.environ:
    app.config.from_envvar('HUBS_CONFIG')

import fedmsg.config
import fedmsg.meta
fedmsg_config = fedmsg.config.load_config()
fedmsg.meta.make_processors(**fedmsg_config)

session = hubs.models.init(fedmsg_config['hubs.sqlalchemy.uri'])
datanommer.models.init(fedmsg_config['datanommer.sqlalchemy.uri'])


class CustomJSONEncoder(flask.json.JSONEncoder):
    def default(self, o):
        try:
            iterable = iter(o)
        except TypeError:
            pass
        else:
            return list(iterable)
        return flask.json.JSONEncoder.default(self, o)

app.json_encoder = CustomJSONEncoder


@app.route('/')
def index():
    if not flask.g.auth.logged_in:
        return flask.redirect(flask.url_for('login_fedora'))

    return flask.redirect(flask.url_for('hub', name=flask.g.auth.nickname))


@app.route('/<name>')
@app.route('/<name>/')
def hub(name):
    hub = get_hub(session, name)
    return flask.render_template('hubs.html', hub=hub, session=session)


@app.route('/<name>/json')
@app.route('/<name>/json/')
def hub_json(name):
    hub = get_hub(session, name)
    response = flask.jsonify(hub.__json__(session))
    # TODO -- modify headers with response.headers['X-fedora-hubs-wat'] = 'foo'
    return response


@app.route('/<hub>/<idx>')
@app.route('/<hub>/<idx>/')
def widget_render(hub, idx):
    widget = get_widget(session, hub, idx)
    return widget.render(session)


@app.route('/<hub>/<idx>/json')
@app.route('/<hub>/<idx>/json/')
def widget_json(hub, idx):
    widget = get_widget(session, hub, idx)
    response = flask.jsonify(widget.__json__(session))
    # TODO -- modify headers with response.headers['X-fedora-hubs-wat'] = 'foo'
    return response


@app.route('/source/<name>')
@app.route('/source/<name>/')
def widget_source(name):
    from hubs.widgets import registry
    base = '/hubs/'
    fname = base + registry[name].__file__.split(base, 1)[1]
    fname = fname.replace('.pyc', '.py')
    return flask.redirect(SOURCE_URL + fname)


# Set up OpenID in stateless mode
oid = OpenID(app,
             safe_roots=[],
             store_factory=lambda: None,
             url_root_as_trust_root=True)


@app.route('/login/', methods=('GET', 'POST'))
@app.route('/login', methods=('GET', 'POST'))
@oid.loginhandler
def login():
    default = flask.url_for('index')
    next_url = flask.request.args.get('next', default)
    if flask.g.auth.logged_in:
        return flask.redirect(next_url)

    openid_server = flask.request.form.get('openid', None)
    if openid_server:
        return oid.try_login(
            openid_server, ask_for=['email', 'fullname', 'nickname'],
            ask_for_optional=[])

    return flask.render_template(
        'login.html', next=oid.get_next_url(), error=oid.fetch_error())


@app.route('/login/fedora/')
@app.route('/login/fedora')
@oid.loginhandler
def login_fedora():
    #default = flask.url_for('profile_redirect')
    #next_url = flask.request.args.get('next', default)
    return oid.try_login(
        'https://id.fedoraproject.org',
        ask_for=['email', 'fullname', 'nickname'],
        ask_for_optional=[])


@app.route('/logout/')
@app.route('/logout')
def logout():
    if 'openid' in flask.app.session:
        flask.app.session.pop('openid')
    return flask.redirect(flask.url_for('index'))


@oid.after_login
def after_openid_login(resp):
    default = flask.url_for('index')
    if not resp.identity_url:
        return flask.redirect(default)

    openid_url = resp.identity_url
    flask.app.session['openid'] = openid_url
    flask.app.session['fullname'] = resp.fullname
    flask.app.session['nickname'] = resp.nickname or resp.fullname
    flask.app.session['email'] = resp.email

    openid = openid_url.strip('/').split('/')[-1]
    hubs.models.User.get_or_create(
        session, openid=openid, fullname=resp.fullname)

    next_url = flask.request.args.get('next', default)
    return flask.redirect(next_url)


def login_required(function):
    """ Flask decorator to restrict access to logged-in users. """
    @functools.wraps(function)
    def decorated_function(*args, **kwargs):
        """ Decorated function, actually does the work. """
        if not flask.g.auth.logged_in:
            flask.flash('Login required', 'errors')
            return flask.redirect(flask.url_for(
                'login_fedora', next=flask.request.url))

        return function(*args, **kwargs)
    return decorated_function


@app.before_request
def check_auth():
    flask.g.fedmsg_config = fedmsg_config
    flask.g.auth = munch.Munch(logged_in=False)
    if 'openid' in flask.session:
        openid = flask.session.get('openid')
        if isinstance(openid, six.binary_type):
            openid = openid.decode('utf-8')
        openid = openid.strip('/').split('/')[-1]
        flask.g.auth.logged_in = True
        flask.g.auth.openid = openid
        flask.g.auth.user = hubs.models.User.by_openid(session, openid)
        flask.g.auth.openid_url = flask.session.get('openid')
        flask.g.auth.fullname = flask.session.get('fullname', None)
        flask.g.auth.nickname = flask.session.get('nickname', None)
        flask.g.auth.email = flask.session.get('email', None)


def get_hub(session, name):
    """ Utility shorthand to get a hub and 404 if not found. """
    hub = session.query(hubs.models.Hub)\
        .filter(hubs.models.Hub.name==name)\
        .first()

    if not hub:
        flask.abort(404)

    return hub


def get_widget(session, hub, idx):
    """ Utility shorthand to get a widget and 404 if not found. """
    try:
        idx = int(idx)
    except TypeError:
        flask.abort(404)

    hub = get_hub(session, hub)

    for widget in hub.widgets:
        if widget.idx == idx:
            return widget

    flask.abort(404)


## Here are a bunch of API methods that should probably be broken out into
## their own file
@app.route('/api/hub/<hub>/subscribe', methods=['POST'])
@login_required
def hub_subscribe(hub):
    hub = get_hub(session, hub)
    user = hubs.models.User.by_openid(session, flask.g.auth.openid)
    hub.subscribe(session, user)
    session.commit()
    return flask.redirect(flask.url_for('hub', name=hub.name))

@app.route('/api/hub/<hub>/unsubscribe', methods=['POST'])
@login_required
def hub_unsubscribe(hub):
    hub = get_hub(session, hub)
    user = hubs.models.User.by_openid(session, flask.g.auth.openid)
    try:
        hub.unsubscribe(session, user)
    except KeyError:
        return flask.abort(400)
    session.commit()
    return flask.redirect(flask.url_for('hub', name=hub.name))

@app.route('/api/hub/<hub>/join', methods=['POST'])
@login_required
def hub_join(hub):
    hub = get_hub(session, hub)
    user = hubs.models.User.by_openid(session, flask.g.auth.openid)
    hub.subscribe(session, user, role='member')
    session.commit()
    return flask.redirect(flask.url_for('hub', name=hub.name))

@app.route('/api/hub/<hub>/leave', methods=['POST'])
@login_required
def hub_leave(hub):
    hub = get_hub(session, hub)
    user = hubs.models.User.by_openid(session, flask.g.auth.openid)
    try:
        hub.unsubscribe(session, user, role='member')
    except KeyError:
        return flask.abort(400)
    session.commit()
    return flask.redirect(flask.url_for('hub', name=hub.name))


if __name__ == '__main__':
    app.run(debug=True)
