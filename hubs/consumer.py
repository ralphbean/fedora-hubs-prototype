# The fedora hubs backend daemon

import collections
import threading
import time

import fedmsg.consumers

import hubs.models

from hubs.widgets.base import invalidate_cache

import logging
log = logging.getLogger("hubs")


class CacheInvalidatorExtraordinaire(fedmsg.consumers.FedmsgConsumer):
    topic = '*'
    config_key = 'hubs.consumer.enabled'

    def __init__(self, *args, **kwargs):
        log.info("CacheInvalidatorExtraordinaire initializing")
        super(CacheInvalidatorExtraordinaire, self).__init__(*args, **kwargs)

        self.uri = self.hub.config.get('hubs.sqlalchemy.uri', None)
        self.junk_suffixes = self.hub.config.get('hubs.junk_suffixes', [])

        if not self.uri:
            raise ValueError('hubs.sqlalchemy.uri must be present')

        self.hint_cache_lock = threading.Lock()
        session = self.make_session()
        with self.hint_cache_lock:
            self.rebuild_hubs_hint_caches(session)
        session.commit()  # transaction is committed here
        session.close()

        log.info("CacheInvalidatorExtraordinaire initialized")

    def make_session(self):
        return hubs.models.init(self.uri)

    def rebuild_hubs_hint_caches(self, session):
        self.checks_by_topic = collections.defaultdict(list)
        self.checks_by_category = collections.defaultdict(list)
        self.checks_by_username = collections.defaultdict(list)

        widgets = session.query(hubs.models.Widget).all()
        log.info("Building lookup from  %i total widgets" % len(widgets))
        for widget in widgets:
            check = widget.module.should_invalidate

            if not hasattr(check, 'hints'):
                raise AttributeError("%r must declare hints" % widget.module)

            for topic in check.hints['topics']:
                self.checks_by_topic[topic].append((check, widget,))

            for category in check.hints['categories']:
                self.checks_by_category[category].append((check, widget,))

            usernames = check.hints['usernames_function'](widget)
            for username in usernames:
                self.checks_by_username[username].append((check, widget,))

    @property
    def cache_initialized(self):
        return self.checks_by_topic and self.checks_by_category

    def consume(self, raw_msg):
        session = self.make_session()
        try:
            self.work(session, raw_msg)
            session.commit()  # transaction is committed here
        except:
            session.rollback()  # rolls back the transaction
            raise

    def work(self, session, raw_msg):
        topic, msg = raw_msg['topic'], raw_msg['body']
        category = topic.split('.')[3]

        for suffix in self.junk_suffixes:
            if topic.endswith(suffix):
                log.info("Dropping %r", topic)
                return

        start = time.time()
        log.info("CacheInvalidatorExtraordinaire received %s %s",
                  msg['msg_id'], msg['topic'])

        if category == 'hubs' or not self.cache_initialized:
            # Someone has modified an object in the hubs database, so let's
            # rebuild our cache of our own database.
            with self.hint_cache_lock:
                self.rebuild_hubs_hint_caches(session)

        # Begin our real work.
        # Find which widgets should have their caches nuked and make it so.

        # Start this by finding a subset of widget checks that might match this
        # message. Look them up based on the hints they declare.
        checks = set(
            self.checks_by_topic[topic] + self.checks_by_category[category]
        )
        log.info("Found %i checks to try for this message" % len(checks))

        # Then, with that hopefully smaller list of checks, try them all and
        # see if any tell us that we should nuke various data caches.
        for check, widget in checks:
            if check(msg, session, widget):
                log.info("! Invalidating cache for %r" % widget)
                # Invalidate the cache...
                invalidate_cache(widget.module, **widget.config)
                # Rebuild it.
                widget.module.data(session, widget, **widget.config)
                # TODO -- fire off an EventSource notice that we updated stuff

        log.info("Done.  %0.2fs %s %s",
                  time.time() - start, msg['msg_id'], msg['topic'])

    def stop(self):
        log.info("Cleaning up CacheInvalidatorExtraordinaire.")
        super(CacheInvalidatorExtraordinaire, self).stop()
