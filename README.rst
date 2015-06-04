Hacking
-------

Hubs should work on python2 **and** python3, so let's default to python3 and
see how that goes.

Setup a python virtualenv::

    $ sudo yum install python-virtualenvwrapper
    $ mkvirtualenv --python=$(which python3) hubs

Install the dependencies from PyPI::

    $ pip install -r requirements.txt

Try running it with::

    $ PYTHONPATH=. python3 populate.py  # To create the db
    $ PYTHONPATH=. python3 hubs/app.py  # To run the dev server

And then navigate to http://localhost:5000/designteam

If you want to test it with 8 worker threads, try ``gunicorn``::

    $ pip install gunicorn
    $ gunicorn -w 8 hubs.app:app

Internal design
---------------

There's no authn or user information at all currently.  There are only:

- widgets
- hubs (which are just collections of widgets)

How things are currently (they don't have to stay this way):

You write a new widget in the ``hubs/widgets/`` directory and must declare it
in the registry dict in ``hubs/widgets/__init__.py``.

In order to be valid, a widget must have:

- A ``data(request, session, widgets, **kwargs)`` function that returns a
  jsonifiable dict of data.  This will get cached -- more on that later.
- A ``template`` object that is a jinja2 template for that widget.
- Optionally, a ``chrome`` decorator.

This isn't implemented yet, but they're going to need:

- A ``should_invalidate(message, session, widget)`` function that will be used to
  *potentially* invalidate the widget's cache. That function will get called by
  a backend daemon listening for fedmsg messages so when you update your group
  memberships in FAS, a fedmsg message hits the fedora-hubs backend and returns
  True if the lookup value should be nuked/refreshed in memcached (or some
  other store).

Furthermore, a proposal:

- The template per-widget is currently held and rendered *server-side* with
  jinja2.  This is how all our apps do it, more or less.

  We might want to consider using handlebars.js for our templates instead and
  rendering all of the widgets asynchronously on the client.  It could be cool,
  but is new-ground for our team.

Still more proposals:

- We could re-use the existing websocket service we have at
  wss://hub.fedoraproject.org:9939 but it has some problems:
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

This is more "proposal" territory.  None of this is implemented, but here are
some more details on how the whole thing should work together.

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
