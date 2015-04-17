import os

import flask

import models

app = flask.Flask(__name__)


app.config.from_object('default_config')
if 'HUBS_CONFIG' in os.environ:
    app.config.from_envvar('HUBS_CONFIG')


@app.route('/')
def index():
    return flask.redirect('/designteam')  # TODO - remove this later


@app.route('/<hub_name>')
@app.route('/<hub_name>/')
def hubs_view(hub_name):
    session = models.init(app.config['DB_URL'])
    hub = session.query(models.Hub)\
        .filter(models.Hub.name==hub_name)\
        .first()

    return flask.render_template('hubs.html', hub=hub, session=session)


if __name__ == '__main__':
    app.run(debug=True)
