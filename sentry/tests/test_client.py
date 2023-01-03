# Copyright 2016-2017 Versada <https://versada.eu/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import sys
from unittest.mock import patch

from sentry_sdk.integrations.logging import _IGNORED_LOGGERS
from sentry_sdk.transport import HttpTransport

from odoo import exceptions
from odoo.tests import TransactionCase
from odoo.tools import config

from ..hooks import initialize_sentry

GIT_SHA = "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
RELEASE = "test@1.2.3"


def remove_handler_ignore(handler_name):
    """Removes handlers of handlers ignored list."""
    _IGNORED_LOGGERS.discard(handler_name)


class TestException(exceptions.UserError):
    pass


class InMemoryTransport(HttpTransport):
    """A :class:`sentry_sdk.Hub.transport` subclass which simply stores events in a list.

    Extended based on the one found in raven-python to avoid additional testing
    dependencies: https://git.io/vyGO3
    """

    def __init__(self, *args, **kwargs):
        self.events = []
        self.envelopes = []

    def capture_event(self, event, *args, **kwargs):
        self.events.append(event)

    def capture_envelope(self, envelope, *args, **kwargs):
        self.envelopes.append(envelope)

    def has_event(self, event_level, event_msg):
        for event in self.events:
            if (
                event.get("level") == event_level
                and event.get("logentry", {}).get("message") == event_msg
            ):
                return True
        return False

    def flush(self, *args, **kwargs):
        pass

    def kill(self, *args, **kwargs):
        pass


class TestClientSetup(TransactionCase):
    def setUp(self):
        super(TestClientSetup, self).setUp()
        self.dsn = "http://public:secret@example.com/1"
        config.options["sentry_enabled"] = True
        config.options["sentry_dsn"] = self.dsn
        self.client = initialize_sentry(config)._client
        self.client.transport = InMemoryTransport({"dsn": self.dsn})
        self.handler = self.client.integrations["logging"]._handler

    def log(self, level, msg, exc_info=None):
        record = logging.LogRecord(__name__, level, __file__, 42, msg, (), exc_info)
        self.handler.emit(record)

    def assertEventCaptured(self, client, event_level, event_msg):
        self.assertTrue(
            client.transport.has_event(event_level, event_msg),
            msg='Event: "%s" was not captured' % event_msg,
        )

    def assertEventNotCaptured(self, client, event_level, event_msg):
        self.assertFalse(
            client.transport.has_event(event_level, event_msg),
            msg='Event: "%s" was captured' % event_msg,
        )

    def test_initialize_raven_sets_dsn(self):
        self.assertEqual(self.client.dsn, self.dsn)

    def test_capture_event(self):
        level, msg = logging.WARNING, "Test event, can be ignored"
        self.log(level, msg)
        level = "warning"
        self.assertEventCaptured(self.client, level, msg)

    def test_capture_event_exc(self):
        level, msg = logging.WARNING, "Test event, can be ignored exception"
        try:
            raise TestException(msg)
        except TestException:
            exc_info = sys.exc_info()
        self.log(level, msg, exc_info)
        level = "warning"
        self.assertEventCaptured(self.client, level, msg)

    def test_ignore_exceptions(self):
        config.options["sentry_ignore_exceptions"] = "odoo.exceptions.UserError"
        client = initialize_sentry(config)._client
        client.transport = InMemoryTransport({"dsn": self.dsn})
        level, msg = logging.WARNING, "Test exception"
        try:
            raise exceptions.UserError(msg)
        except exceptions.UserError:
            exc_info = sys.exc_info()
        self.log(level, msg, exc_info)
        level = "warning"
        self.assertEventNotCaptured(client, level, msg)

    def test_exclude_logger(self):
        config.options["sentry_enabled"] = True
        config.options["sentry_exclude_loggers"] = __name__
        client = initialize_sentry(config)._client
        client.transport = InMemoryTransport({"dsn": self.dsn})
        level, msg = logging.WARNING, "Test exclude logger %s" % __name__
        self.log(level, msg)
        level = "warning"
        # Revert ignored logger so it doesn't affect other tests
        remove_handler_ignore(__name__)
        self.assertEventNotCaptured(client, level, msg)

    @patch("odoo.addons.sentry.hooks.get_odoo_commit", return_value=GIT_SHA)
    def test_config_odoo_dir(self, get_odoo_commit):
        config.options["sentry_odoo_dir"] = "/opt/odoo/core"
        client = initialize_sentry(config)._client

        self.assertEqual(
            client.options["release"],
            GIT_SHA,
            "Failed to use 'sentry_odoo_dir' parameter appropriately",
        )

    @patch("odoo.addons.sentry.hooks.get_odoo_commit", return_value=GIT_SHA)
    def test_config_release(self, get_odoo_commit):
        config.options["sentry_odoo_dir"] = "/opt/odoo/core"
        config.options["sentry_release"] = RELEASE
        client = initialize_sentry(config)._client

        self.assertEqual(
            client.options["release"],
            RELEASE,
            "Failed to use 'sentry_release' parameter appropriately",
        )
