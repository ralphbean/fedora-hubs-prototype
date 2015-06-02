# The fedora hubs backend daemon

import time
import random

import fedmsg.consumers

import hubs.models

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

        log.info("CacheInvalidatorExtraordinaire initialized")

    def make_session(self):
        return hubs.models.init(self.uri)

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

        for suffix in self.junk_suffixes:
            if topic.endswith(suffix):
                log.info("Dropping %r", topic)
                return

        start = time.time()
        log.info("CacheInvalidatorExtraordinaire received %s %s",
                  msg['msg_id'], msg['topic'])

        # Begin our real work.
        # Find which widgets should have their caches nuked and make it so.

        # First, make a thread-local copy of the widgets.
        widgets = list(session.query(hubs.models.Widget).all())
        log.info("Comparing message against %i widgets" % len(widgets))

        # Shuffle it so that not all threads step through the list in the same
        # order.  This should cut down on competition for the dogpile lock.
        random.shuffle(widgets)

        # And do the real work of comparing every widget against the message.
        for widget in widgets:
            if widget.module.should_invalidate(msg, session, widget):
                raise NotImplementedError("Invalidate the cache...")
                raise NotImplementedError("Rebuild it.")

        log.info("Done.  %0.2fs %s %s",
                  time.time() - start, msg['msg_id'], msg['topic'])

    def stop(self):
        log.info("Cleaning up CacheInvalidatorExtraordinaire.")
        super(CacheInvalidatorExtraordinaire, self).stop()
