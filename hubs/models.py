# -*- coding: utf-8 -*-
#
# Copyright © 2015  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU Lesser General Public License (LGPL) version 2, or
# (at your option) any later version.  This program is distributed in the
# hope that it will be useful, but WITHOUT ANY WARRANTY expressed or
# implied, including the implied warranties of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
# more details.  You should have received a copy of the GNU Lesser General
# Public License along with this program; if not, write to the Free
# Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#


import datetime
import json
import logging

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import relation
from sqlalchemy.orm import backref

import fedmsg
import fedmsg.utils

import hubs.defaults
import hubs.widgets
from hubs.utils import username2avatar


class HubsBase(object):
    def notify(self, openid, changed):
        obj = type(self).__name__.lower()
        topic = obj + ".update"
        fedmsg.publish(
            topic=topic,
            msg=dict(
                openid=openid,
                changed=changed,
            )
        )


BASE = declarative_base(cls=HubsBase)

log = logging.getLogger(__name__)


placekitten = lambda: "https://placekitten.com/g/320/320"


def init(db_url, debug=False, create=False):
    """ Create the tables in the database using the information from the
    url obtained.

    :arg db_url, URL used to connect to the database. The URL contains
        information with regards to the database engine, the host to
        connect to, the user and password and the database name.
          ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg debug, a boolean specifying whether we should have the verbose
        output of sqlalchemy or not.
    :return a session that can be used to query the database.

    """
    engine = create_engine(db_url, echo=debug)

    if create:
        BASE.metadata.create_all(engine)

    return scoped_session(sessionmaker(bind=engine))


roles = ['subscriber', 'member', 'owner', 'stargazer']


class Association(BASE):
    __tablename__ = 'association'

    hub_id = sa.Column(sa.String(50),
                       sa.ForeignKey('hubs.name'),
                       primary_key=True)
    user_id = sa.Column(sa.Text,
                        sa.ForeignKey('users.openid'),
                        primary_key=True)
    role = sa.Column(sa.Enum(*roles), primary_key=True)

    user = relation("User", backref="associations")
    hub = relation("Hub", backref="associations")

    @classmethod
    def get(cls, session, hub, user, role):
        return session.query(cls)\
            .filter_by(hub=hub)\
            .filter_by(user=user)\
            .filter_by(role=role)\
            .first()


class Hub(BASE):
    __tablename__ = 'hubs'
    name = sa.Column(sa.String(50), primary_key=True)
    summary = sa.Column(sa.String(128))
    created_on = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    widgets = relation('Widget', backref=backref('hub'))
    left_width = sa.Column(sa.Integer, nullable=False, default=8)

    # A URL to the "avatar" for this hub.
    avatar = sa.Column(sa.String(256), default=placekitten)

    #fas_group = sa.Column(sa.String(32), nullable=False)

    @property
    def owners(self):
        return [assoc.user for assoc in self.associations
                if assoc.role == 'owner']

    @property
    def members(self):
        return [assoc.user for assoc in self.associations
                if assoc.role == 'member' or assoc.role =='owner']

    @property
    def subscribers(self):
        return [assoc.user for assoc in self.associations
                if assoc.role == 'subscriber']

    @property
    def stargazers(self):
        return [assoc.user for assoc in self.associations
                if assoc.role == 'stargazer']

    def subscribe(self, session, user, role='subscriber'):
        """ Subscribe a user to this hub. """
        # TODO -- add logic here to manage not adding the user multiple
        # times, doing different roles, etc.. publish a fedmsg message,
        # etc...
        session.add(Association(user=user, hub=self, role=role))
        session.commit()

    def unsubscribe(self, session, user, role='subscriber'):
        """ Subscribe a user to this hub. """
        # TODO -- add logic here to manage not adding the user multiple
        # times, doing different roles, etc.. publish a fedmsg message,
        # etc...
        association = Association.get(session, hub=self, user=user, role=role)
        if not association:
            raise KeyError("%r is not a %r of %r" % (user, role, self))
        session.delete(association)
        session.commit()


    @classmethod
    def by_name(cls, session, name):
        return session.query(cls).filter_by(name=name).first()

    get = by_name

    @classmethod
    def create_user_hub(cls, session, username, fullname):
        hub = cls(name=username, summary=fullname,
                  avatar=username2avatar(username))
        session.add(hub)
        hubs.defaults.add_user_widgets(session, hub, username, fullname)

    @property
    def right_width(self):
        return 12 - self.left_width

    @property
    def left_widgets(self):
        return sorted(
            [w for w in self.widgets if w.left],
            key=lambda w: w.index)

    @property
    def right_widgets(self):
        return sorted(
            [w for w in self.widgets if not w.left],
            key=lambda w: w.index)

    def __json__(self, session):
        return {
            'name': self.name,
            'summary': self.summary,

            # TODO -- splash image

            'widgets': [widget.idx for widget in self.widgets],
            'left_width': self.left_width,

            # TODO -- these three need to be fleshed out with real fas data.
            'owners': self.owners,
            'members': self.members,
            'subscribers': self.subscribers,
        }

def _config_default(context):
    plugin_name = context.current_parameters['plugin']
    plugin = hubs.widgets.registry[plugin_name]
    arguments = getattr(plugin.data, 'widget_arguments', [])
    return json.dumps(dict([(arg.name, arg.default) for arg in arguments]))


class Widget(BASE):
    __tablename__ = 'widgets'
    idx = sa.Column(sa.Integer, primary_key=True)
    plugin = sa.Column(sa.String(50), nullable=False)
    created_on = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    hub_id = sa.Column(sa.String(50), sa.ForeignKey('hubs.name'))
    _config = sa.Column(sa.String(256), default=_config_default)

    index = sa.Column(sa.Integer, nullable=False)
    left = sa.Column(sa.Boolean, nullable=False, default=False)

    @property
    def config(self):
        return json.loads(self._config)

    @config.setter
    def config_setter(self, config):
        self._config = json.dumps(config)

    def __json__(self, session):
        module = hubs.widgets.registry[self.plugin]
        data = module.data(session, self, **self.config)
        return {
            'id': self.idx,
            # TODO -- use flask.url_for to get the url for this widget
            'plugin': self.plugin,
            'description': module.__doc__,
            'hub': self.hub_id,
            'left': self.left,
            'index': self.index,
            'data': data,
            'config': self.config,
        }

    @property
    def module(self):
        return hubs.widgets.registry[self.plugin]

    def render(self, session):
        render = hubs.widgets.render
        return render(self.module, session, self, **self.config)


class User(BASE):
    __tablename__ = 'users'
    openid = sa.Column(sa.Text, primary_key=True)
    fullname = sa.Column(sa.Text)
    created_on = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)


    def __json__(self, session):
        return {
            'username': self.username,
            'openid': self.openid,
            'avatar': username2avatar(self.username),
            'fullname': self.fullname,
            'created_on': self.created_on,
            # We'll need hubs subscribed to, owned, etc..
            #'hubs': [hub.idx for hub in self.hubx],
        }

    @property
    def ownerships(self):
        return [assoc.hub for assoc in self.associations
                if assoc.role == 'owner']
    @property
    def memberships(self):
        return [assoc.hub for assoc in self.associations
                if assoc.role == 'member' or assoc.role =='owner']

    @property
    def subscriptions(self):
        return [assoc.hub for assoc in self.associations
                if assoc.role == 'subscriber']

    @property
    def starred_hubs(self):
        return [assoc.hub for assoc in self.associations
                if assoc.role == 'stargazer']

    @property
    def bookmarks(self):
        # TODO -- someday make this editable/configurable.
        return sorted(list(set([assoc.hub for assoc in self.associations
                if assoc.role == 'member'
                or assoc.role == 'subscriber'
                or assoc.role == 'owner'])))

    @property
    def username(self):
        return self.openid.split('.')[0]

    @classmethod
    def by_username(cls, session, username):
        return cls.by_openid(session, "%s.id.fedoraproject.org" % username)

    @classmethod
    def by_openid(cls, session, openid):
        return session.query(cls).filter_by(openid=openid).first()

    get = by_openid

    @classmethod
    def all(cls, session):
        return session.query(cls).all()

    @classmethod
    def get_or_create(cls, session, openid, fullname):
        if not openid:
            raise ValueError("Must provide openid, not %r" % openid)

        self = cls.by_openid(session, openid)
        if not self:
            self = cls(openid=openid, fullname=fullname)
            session.add(self)
            if not Hub.by_name(session, self.username):
                Hub.create_user_hub(session, self.username, self.fullname)

            session.commit()
        return self
