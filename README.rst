Hacking
-------

Setup a python virtualenv::

    $ sudo yum install python-virtualenvwrapper
    $ mkvirtualenv hubs

Install the dependencies from PyPI::

    $ pip install -r requirements.txt

Try running it with::

    $ PYTHONPATH=. python populate.py  # To create the db
    $ PYTHONPATH=. python hubs/app.py  # To run the dev server

And then navigate to http://localhost:5000/designteam
