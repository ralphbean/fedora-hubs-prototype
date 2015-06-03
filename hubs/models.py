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

import hubs.widgets


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


class Hub(BASE):
    __tablename__ = 'hubs'
    name = sa.Column(sa.String(50), primary_key=True)
    summary = sa.Column(sa.String(128))
    created_on = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)
    widgets = relation('Widget', backref=backref('hub'))
    left_width = sa.Column(sa.Integer, nullable=False, default=8)

    #fas_group = sa.Column(sa.String(32), nullable=False)

    # This is just some silly dev data.  eventually, connect this
    # to real database data.
    owners = ['tatica', 'gnokii', 'duffy', 'ryanlerch']
    members = ['ralph', 'sadin', 'sayan'] + owners
    subscribers = []

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

    def __json__(self, reify=False):
        return {
            'name': self.name,
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

    def __json__(self, reify=False):
        return {
            'plugin': self.plugin,
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
    openid_url = sa.Column(sa.Text, unique=True)
    created_on = sa.Column(sa.DateTime, default=datetime.datetime.utcnow)

    def __json__(self, reify=False):
        return {
            'openid': self.openid,
            'openid_url': self.openid_url,
            'created_on': self.created_on,
        }

    @classmethod
    def by_openid(cls, session, openid):
        return session.query(cls).filter_by(openid=openid).first()

    get = by_openid

    @classmethod
    def all(cls, session):
        return session.query(cls).all()
