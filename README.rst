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

Furthermore:

- The template per-widget is currently held and rendered *server-side* with
  jinja2.  This is how all our apps do it, more or less.

  We might want to consider using handlebars.js for our templates instead and
  rendering all of the widgets asynchronously on the client.  It could be cool,
  but is new-ground for our team.
