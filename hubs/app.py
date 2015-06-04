import functools
import os

import flask
import munch

from flask.ext.openid import OpenID

import hubs.models

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

session = hubs.models.init(fedmsg_config['hubs.sqlalchemy.uri'])


@app.route('/')
def index():
    if not flask.g.auth.logged_in:
        return flask.redirect(flask.url_for('login_fedora'))

    return flask.redirect(flask.url_for('hub', name=flask.g.auth.nickname))


@app.route('/<name>')
@app.route('/<name>/')
def hub(name):
    hub = session.query(hubs.models.Hub)\
        .filter(hubs.models.Hub.name==name)\
        .first()

    if not hub:
        flask.abort(404)

    return flask.render_template('hubs.html', hub=hub, session=session)


def get_widget(session, hub, idx):
    try:
        idx = int(idx)
    except TypeError:
        flask.abort(404)

    hub = session.query(hubs.models.Hub)\
        .filter(hubs.models.Hub.name==hub)\
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
    widget = get_widget(session, hub, idx)
    return widget.render(session)


@app.route('/<hub>/<idx>/json')
@app.route('/<hub>/<idx>/json/')
def widget_json(hub, idx):
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
    flask.g.auth = munch.Munch(
        logged_in=False,
        method=None,
        id=None,
    )
    if 'openid' in flask.session:
        openid = flask.session.get('openid').strip('/').split('/')[-1]
        flask.g.auth.logged_in = True
        flask.g.auth.method = u'openid'
        flask.g.auth.openid = openid
        flask.g.auth.openid_url = flask.session.get('openid')
        flask.g.auth.fullname = flask.session.get('fullname', None)
        flask.g.auth.nickname = flask.session.get('nickname', None)
        flask.g.auth.email = flask.session.get('email', None)



if __name__ == '__main__':
    app.run(debug=True)
