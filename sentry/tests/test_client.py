# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import sys
import unittest

import raven
from mock import patch

from odoo import exceptions

from .. import initialize_raven
from ..logutils import OdooSentryHandler

GIT_SHA = "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
RELEASE = "test@1.2.3"


def log_handler_by_class(logger, handler_cls):
    for handler in logger.handlers:
        if isinstance(handler, handler_cls):
            yield handler


def remove_logging_handler(logger_name, handler_cls):
    """Removes handlers of specified classes from a :class:`logging.Logger`
    with a given name.

    :param string logger_name: name of the logger

    :param handler_cls: class of the handler to remove. You can pass a tuple of
        classes to catch several classes
    """
    logger = logging.getLogger(logger_name)
    for handler in log_handler_by_class(logger, handler_cls):
        logger.removeHandler(handler)


class InMemoryClient(raven.Client):
    """A :class:`raven.Client` subclass which simply stores events in a list.

    Extended based on the one found in raven-python to avoid additional testing
    dependencies: https://git.io/vyGO3
    """

    def __init__(self, **kwargs):
        self.events = []
        super(InMemoryClient, self).__init__(**kwargs)

    def is_enabled(self):
        return True

    def send(self, **kwargs):
        self.events.append(kwargs)

    def has_event(self, event_level, event_msg):
        for event in self.events:
            if event.get("level") == event_level and event.get("message") == event_msg:
                return True
        return False


class TestClientSetup(unittest.TestCase):
    def setUp(self):
        super(TestClientSetup, self).setUp()
        self.logger = logging.getLogger(__name__)

        # Sentry is enabled by default, so the default handler will be added
        # when the module is loaded. After that, subsequent calls to
        # setup_logging will not re-add our handler. We explicitly remove
        # OdooSentryHandler handler so we can test with our in-memory client.
        remove_logging_handler("", OdooSentryHandler)

    def assertEventCaptured(self, client, event_level, event_msg):
        self.assertTrue(
            client.has_event(event_level, event_msg),
            msg='Event: "%s" was not captured' % event_msg,
        )

    def assertEventNotCaptured(self, client, event_level, event_msg):
        self.assertFalse(
            client.has_event(event_level, event_msg),
            msg='Event: "%s" was captured' % event_msg,
        )

    def test_initialize_raven_sets_dsn(self):
        config = {
            "sentry_enabled": True,
            "sentry_dsn": "http://public:secret@example.com/1",
        }
        client = initialize_raven(config, client_cls=InMemoryClient)
        self.assertEqual(client.remote.base_url, "http://example.com")

    def test_capture_event(self):
        config = {
            "sentry_enabled": True,
            "sentry_dsn": "http://public:secret@example.com/1",
        }
        level, msg = logging.WARNING, "Test event, can be ignored"
        client = initialize_raven(config, client_cls=InMemoryClient)
        self.logger.log(level, msg)
        self.assertEventCaptured(client, level, msg)

    def test_ignore_exceptions(self):
        config = {
            "sentry_enabled": True,
            "sentry_dsn": "http://public:secret@example.com/1",
            "sentry_ignore_exceptions": "odoo.exceptions.UserError",
        }
        level, msg = logging.WARNING, "Test UserError"
        client = initialize_raven(config, client_cls=InMemoryClient)

        handlers = list(log_handler_by_class(logging.getLogger(), OdooSentryHandler))
        self.assertTrue(handlers)
        handler = handlers[0]
        try:
            raise exceptions.UserError(msg)
        except exceptions.UserError:
            exc_info = sys.exc_info()
        record = logging.LogRecord(__name__, level, __file__, 42, msg, (), exc_info)
        handler.emit(record)
        self.assertEventNotCaptured(client, level, msg)

    @patch("odoo.addons.sentry.get_odoo_commit", return_value=GIT_SHA)
    def test_config_odoo_dir(self, get_odoo_commit):
        config = {
            "sentry_enabled": True,
            "sentry_dsn": "http://public:secret@example.com/1",
            "sentry_odoo_dir": "/opt/odoo/core",
        }
        client = initialize_raven(config, client_cls=InMemoryClient)
        self.assertEqual(
            client.release,
            GIT_SHA,
            "Failed to use 'sentry_odoo_dir' parameter appropriately",
        )

    @patch("odoo.addons.sentry.get_odoo_commit", return_value=GIT_SHA)
    def test_config_release(self, get_odoo_commit):
        config = {
            "sentry_enabled": True,
            "sentry_dsn": "http://public:secret@example.com/1",
            "sentry_odoo_dir": "/opt/odoo/core",
            "sentry_release": RELEASE,
        }
        client = initialize_raven(config, client_cls=InMemoryClient)
        self.assertEqual(
            client.release,
            RELEASE,
            "Failed to use 'sentry_release' parameter appropriately",
        )
