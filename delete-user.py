#!/usr/bin/env python
""" Delete a user from the db.

Useful for testing what happens when you recreate them.
"""

import sys

import fedmsg.config
fedmsg_config = fedmsg.config.load_config()

import hubs.models

session = hubs.models.init(fedmsg_config['hubs.sqlalchemy.uri'])

username = raw_input('What user do you want to delete: ')
openid = '%s.id.fedoraproject.org' % username
print "Looking for account %r" % openid
user = hubs.models.User.get(session, openid)
if not user:
    print "No such user %r" % openid
    sys.exit(1)

print "Found %r.  Deleting." % user
session.delete(user)
session.commit()
