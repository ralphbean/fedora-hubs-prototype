import flask

import models

app = flask.Flask(__name__)

@app.route('/')
def index():
    return "hi there"


@app.route('/<hub_name>')
def hubs_view(hub_name):
    session = models.init('sqlite:////var/tmp/hubs.db')
    hub = session.query(models.Hub)\
        .filter(models.Hub.name==hub_name)\
        .first()

    return flask.render_template('hubs.html', hub=hub, session=session)


if __name__ == '__main__':
    app.run(debug=True)
