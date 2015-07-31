Source on Pagure.io
===================

The latest source is not on GitHub, it is on pagure.io.  You can find it at https://pagure.io/fedora-hubs

Hacking
=======
Install fedora dependencies::

    $ sudo dnf install gcc gcc-c++ sqlite-devel 

Hubs should work on either python2 **or** python3.  These instructions will
show the way for python2 only, though.

Setup a python virtualenv::

    $ sudo dnf install python-virtualenvwrapper postgresql postgresql-devel
    $ mkvirtualenv hubs

If the mkvirtualenv command returns "command not found..." you may need to
refresh your bash profile::

    $ source ~/.bashrc

Install the dependencies from PyPI::

    $ pip install -r requirements.txt

Give fedora-hubs some FAS credentials.  It's going to need these to query FAS
for information about other users.  When we deploy this thing to production,
we'll use a system account for this but for now, just use your personal
account.  Copy the following into a new file under the fedmsg.d directory
called fas_credentials.py (``fedmsg.d/fas_credentials.py``) ::

    config = {
        'fas_credentials': {
            'username': 'YOUR_FAS_USERNAME_GOES_HERE',
            'password': 'YOUR_FAS_PASSWORD_GOES_HERE',
        }
    }

Make sure to leave the '' around you username and password - don't delete them!

With that, try running the app with::

    $ PYTHONPATH=. python populate.py  # To create the db
    $ PYTHONPATH=. python hubs/app.py  # To run the dev server

And then navigate to http://localhost:5000/

If you want to test it with 8 worker threads, try ``gunicorn``::

    $ pip install gunicorn
    $ gunicorn -w 8 -t 60 --log-config logging.ini --reload hubs.app:app

When hacking on widgets, it is useful to have this one-liner handy.  It removes
the db alltogether, re-populates it, and restarts the app::

    $ rm /var/tmp/hubs.db; PYTHONPATH=. python populate.py; gunicorn -w 8 -t 240 --log-config logging.ini hubs.app:app

Feed Widget - the Extra Mile
----------------------------

One widget (the big tamale -- the feed widget) requires more legwork to stand
up.  If you just want to see how hubs works and you want to hack on other
peripheral stuff around it, you don't need to bother with these steps.

The feed widget requires a direct DB connection to the datanommer
database; it can't proxy through datagrepper because it needs more
flexibility.  To get this working, you're going to set up:

- a postgres db
- the datanommer daemon

Start with some required packages::

    $ sudo dnf install postgresql-server python-datanommer-consumer datanommer-commands fedmsg-hub

And there are some support libraries you'll also need::

    $ sudo dnf install python-psycopg2 python-fedmsg-meta-fedora-infrastructure

Now, with packages installed, you need to tell postgres to create its initial filesystem layout::

    $ sudo postgresql-setup initdb

And then, we need to tweak its config to let us connect easily for development::

    $ sudo vim /var/lib/pgsql/data/pg_hba.conf

Change **two lines** from ``ident`` to ``trust``.  These two::

    # IPv4 local connections:
    host    all             all             127.0.0.1/32            trust
    # IPv6 local connections:
    host    all             all             ::1/128                 trust

Start that beast up::

    $ sudo systemctl start postgresql

Now, with the db daemon configured and running, let's configure datanommer.  Edit this file::

    $ sudo vim /etc/fedmsg.d/datanommer.py

And do two things:  1) set enabled to ``True`` and 2) give it a real sqlalchemy url, like this::

    config = {
        'datanommer.enabled': True,
        'datanommer.sqlalchemy.url': 'postgres://postgres:whatever@localhost/datanommer',
    }

Tell postgres that it should create space for a 'datanommer' database with this command::

    $ sudo -u postgres psql -c "CREATE DATABASE datanommer;"

And finally, tell datanommer to create all of its tables in that new db we just created::

    $ datanommer-create-db

Tell the fedmsg-hub daemon to restart itself.  It should pick up datanommer as a plugin and start handing messages to it::

    $ sudo systemctl restart fedmsg-hub

And then, wait a few seconds for a message to get nommed, and then you can
check that it's working by running ``sudo datanommer-stats``.  It should print
out some kind of summary about what kinds of messages are in the db now -- it
will just grow and grow over time::

    $ datanommer-stats
    [2015-07-01 14:33:21][    fedmsg    INFO] buildsys has 70 entries
    [2015-07-01 14:33:21][    fedmsg    INFO] faf has 7 entries
    [2015-07-01 14:33:21][    fedmsg    INFO] copr has 6 entries
    [2015-07-01 14:33:21][    fedmsg    INFO] askbot has 2 entries

**Lastly**, (fingers crossed) start up the fedora-hubs webapp and load your
profile page.  Once there are some messages that get into your local database
that *should* show up on your feed.. they should appear there.  (At very least,
you shouldn't get an error message about that widget being unable to be
displayed).

Stubbing out a new Widget
=========================

You write a new widget in the ``hubs/widgets/`` directory and must declare it
in the registry dict in ``hubs/widgets/__init__.py``.

In order to be valid, a widget must have:

- A ``data(session, widgets, **kwargs)`` function that returns a
  jsonifiable dict of data.  This will get cached -- more on that later.
- A ``template`` object that is a jinja2 template for that widget.
- Optionally, a ``chrome`` decorator.
- A ``should_invalidate(message, session, widget)`` function that will be used to
  *potentially* invalidate the widget's cache. That function will get called by
  a backend daemon listening for fedmsg messages so when you update your group
  memberships in FAS, a fedmsg message hits the fedora-hubs backend and returns
  True if the lookup value should be nuked/refreshed in memcached (or some
  other store).

If you want to try making a new widget:

- Copy an existing one in ``hubs/widgets/``
- Add it to the registry in ``hubs/widgets/__init__.py``
- If you want it to show up on a **user** page, add it to ``hubs/defaults.py``
  in the ``add_user_widgets`` function.
- If you want it to show up on **group** pages, add it to ``populate.py``.

Destroy your database, rebuild it, and re-run the app.  Your widget should show up.

A proposal, client-side templates
=================================

- The template per-widget is currently held and rendered *server-side* with
  jinja2.  This is how all our apps do it, more or less.

  We might want to consider using handlebars.js for our templates instead and
  rendering all of the widgets asynchronously on the client.  It could be cool,
  but is new-ground for our team.

  Furthermore, we should likely use something like angular **or** backbone.js
  to manage the data synchronization with those client-side templates.

Some discussion on how to do pushed updates to web clients:

- We could re-use the existing websocket service we have at
  ``wss://hub.fedoraproject.org:9939`` but it has some problems:
- It is very inflexible.  You can subscribe to fedmsg *topics* and then you
  receive the firehose of those topics. For a widget, we already have to write
  a 'cache invalidation' function that listens for messages and then somehow
  knows to invalidate the cache *for a widget* based on some of those messages.
  If we re-used the firehose on the client, we would have to write that
  function *twice* for *each widget*, once in python to invalidate the server's
  memcached cache when a fedmsg message comes in and once in javascript to tell
  the client to reload and redraw a oprtion of itself when a fedmsg comes in
  over the websocket firehose.
- Instead, let's give fedora-hubs its own *widget-specific* `EventSource
  <https://developer.mozilla.org/en-US/docs/Web/API/EventSource>`_ server that
  we tie in to the server-side cache-invalidation backend code.  I.e., when a
  message comes into the backend, it runs all the cache invalidation checkers
  to see which widgets' caches should be refreshed, and once they are refreshed
  we can emit events over EventSource to tell only *those* widgets on any
  connected clients to redraw themselves.

As an aside, it became clear to me when making the diagram in the next section
that, if we use handlebars.js and get rid of the server-side template
rendering, then 1) the data returned by AJAX requests at page load and 2) the
data pushed by the EventSource server can be *the exact same data*.  It will
simplify and streamline the responsibilities of the pieces if the backend is
worried *only* about these per-widget JSON responses.

A picture is worth...
---------------------

Here are some more details on how the whole thing should work together.

.. figure:: https://raw.githubusercontent.com/ralphbean/fedora-hubs-prototype/develop/docs/diagram.png
   :scale: 50 %
   :alt: A diagram of component interactions

   A diagram of component interactions

Let's talk through how data will flow through the system by asking *what
happens when a user requsts their main hubs page*:

- The user requests the page and the wsgi app responds with some barebones HTML
  and enough javascript to get off the ground.
- The user's browser runs javascript that *subscribes* it to the EventSource server.
- The user's browser runs that javascript, which requests data for each of the
  widgets defined on the page.
- The wsgi app receives those requests and checks to see if the data for any of
  them is *cached in memcached*.  If it is, then it is returned.  If not, then
  the wsgi app executes the ``data(...)`` function of that widget to get the
  response ready.  It is stuffed in memcached for later access and returned.
- The client renders widgets as the data for each of its requests comes back.

Later, what happens when a *trac ticket* is filed that should show up in some widget on their page?

- The ticket is updated on fedorahosted.org and a fedmsg message is fired.
- That is received by the hubs backend, which looks up *all* the cached
  responses that should be invalidated by that event (there is a widget on
  mizmo's page, threebean's page, and on the design hub that should all get
  fresh data because of this change).
- All of those widgets get their cached data nuked.
- All of those widgets get their cached data rebuilt by calling ``data(...)`` on them.
- An EventSource event is fired off for any listening clients that *new data is
  available for widgets X, Y, and Z*.  The data is included in the EventSource
  payload so the clients can immediately redraw without bothering to re-query
  the wsgi app.

What happens when the user is viewing the *design team* hub and
simultaneously, an admin *changes the configuration of a widget on that page*?

- Changing the configuration results in a HTTP POST to the wsgi app.
- The configuration is changed accordingly in the postgres database.
- A fedmsg message is fired off indicating that *the configuration for widget X
  has changed*.
- The wsgi app responds 200 OK to the admin.
- Meanwhile, that fedmsg message is received by the backend which:
- ...looks up the cache key for *widget X with the old configuration* and nukes
  it the cached data.
- ...looks up the cache key for *widget X with the new configuration* and
  builds the cached data by calling ``data(...)`` on the widget.
- An EventSource event is fired off which gets recieved by everyone looking at
  the *design team hub*.  The widget on their pages gets redrawn with data from
  the EventSource event.
