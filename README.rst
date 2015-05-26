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

- A ``invalidate(session, message)`` function that will be used to
  *potentially* invalidate the widget's cache. That function will get called by
  a backend daemon listening for fedmsg messages so when you update your group
  memberships in FAS, a fedmsg message hits the fedora-hubs backend and it
  nukes/refreshes a lookup value in memcached (or some other store).

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

A picture is worth...
---------------------

.. figure:: fedora-hubs-prototype/raw/develop/docs/diagram.png
   :scale: 50 %
   :alt: A diagram of component interactions

   A diagram of component interactions
