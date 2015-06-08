#!/usr/bin/env python
""" Populate the hubs db with lots of data from FAS. """

import getpass
import socket
import string

import hubs.models

import fedora.client.fas2
import fedmsg.config
fedmsg_config = fedmsg.config.load_config()

fasclient = fedora.client.fas2.AccountSystem(
    username=raw_input('Your FAS username: '),
    password=getpass.getpass(),
)
timeout = socket.getdefaulttimeout()
socket.setdefaulttimeout(None)

for letter in reversed(sorted(list(set(string.letters.lower())))):
    session = hubs.models.init(fedmsg_config['hubs.sqlalchemy.uri'], True, True)
    print "Querying FAS for the %r users.. hang on." % letter
    request = fasclient.send_request('/user/list',
                                    req_params={'search': '%s*' % letter},
                                    auth=True,
                                    timeout=500)
    users = request['people']

    for user in users:
        username = user['username']
        fullname = user['human_name']
        openid = '%s.id.fedoraproject.org' % username
        print "Creating account for %r" % openid
        hubs.models.User.get_or_create(
            session, openid=openid, fullname=fullname)

    session.commit()
