# Copyright 2016-2017 Versada <https://versada.eu/>
# Copyright 2026 Therp BV <https://therp.nl/>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import inspect
import logging
import os
import sys
from unittest.mock import patch

from sentry_sdk.integrations.logging import _IGNORED_LOGGERS
from sentry_sdk.integrations.wsgi import SentryWsgiMiddleware
from sentry_sdk.transport import HttpTransport

import odoo.http
from odoo import exceptions
from odoo.tests import TransactionCase

from .. import const
from .. import hooks as sentry_hooks
from ..const import get_options_from_env, to_bool, to_int_if_defined
from ..hooks import before_send, initialize_sentry

GIT_SHA = "d670460b4b4aece5915caf5c68d12f560a9fe3e4"
RELEASE = "test@1.2.3"


def remove_handler_ignore(handler_name):
    """Removes handlers of handlers ignored list."""
    _IGNORED_LOGGERS.discard(handler_name)


class TestException(exceptions.UserError):
    pass


class InMemoryTransport(HttpTransport):
    """A :class:`sentry_sdk.Hub.transport` subclass which simply stores events
    in a list.

    Extended based on the one found in raven-python to avoid additional testing
    dependencies: https://git.io/vyGO3
    """

    def __init__(self, *args, **kwargs):
        self.events = []
        self.envelopes = []

    def capture_envelope(self, envelope, *args, **kwargs):
        self.envelopes.append(envelope)

    def has_event(self, event_level, event_msg):
        for envelope in self.envelopes:
            event = envelope.get_event()
            if (
                event.get("level") == event_level
                and event.get("logentry", {}).get("message") == event_msg
            ):
                return event
        return False

    def flush(self, *args, **kwargs):
        pass

    def kill(self, *args, **kwargs):
        pass


class NoopHandler(logging.Handler):
    """
    A Handler subclass that does nothing with any given log record.

    Sentry's log patching works by having the integration process things after
    the normal log handlers are run, so we use this handler to do nothing and
    move to Sentry logic ASAP.
    """

    def emit(self, record):
        pass


class TestClientSetup(TransactionCase):
    def setUp(self):
        super().setUp()
        self.dsn = "http://public:secret@example.com/1"
        self.clear_env()
        self.patch_config(
            {
                "sentry_enabled": True,
                "sentry_dsn": self.dsn,
                "sentry_logging_level": "error",
            }
        )
        self.client = initialize_sentry(sentry_hooks.sentry_config)._client
        self.client.transport = InMemoryTransport({"dsn": self.dsn})

        # Setup our own logger so we don't flood stderr with error logs
        self.logger = logging.getLogger("odoo.sentry.test.logger")
        # Do not mutate list while iterating it
        handlers = [handler for handler in self.logger.handlers]
        for handler in handlers:
            self.logger.removeHandler(handler)
        self.logger.addHandler(NoopHandler())
        self.logger.propagate = False

    def patch_config(self, options: dict):
        """
        Patch sentry_config with the given `options`, ensuring that the patch
        is undone when the test completes.
        """
        _config_patcher = patch.dict(
            in_dict=sentry_hooks.sentry_config,
            values=options,
        )
        _config_patcher.start()
        self.addCleanup(_config_patcher.stop)

    def patch_env(self, variables: dict):
        """
        Set `variables` in the environment, ensuring that they are unset again
        when the test completes.
        """
        _env_patcher = patch.dict(os.environ, values=variables)
        _env_patcher.start()
        self.addCleanup(_env_patcher.stop)

    def clear_env(self):
        """
        Drop the ODOO_SENTRY_* variables the machine running the tests happens to
        carry, so a test reads the configuration it sets up itself rather than the
        environment of whoever runs it.
        """
        prefix = f"{const.ENV_PREFIX}{const.ENV_OPTION_PREFIX}"
        carried = {k: v for k, v in os.environ.items() if k.startswith(prefix)}
        for key in carried:
            del os.environ[key]
        self.addCleanup(os.environ.update, carried)

    def log(self, level, msg, exc_info=None):
        self.logger.log(level, msg, exc_info=exc_info)

    def assertEventCaptured(self, client, event_level, event_msg):
        self.assertTrue(
            client.transport.has_event(event_level, event_msg),
            msg=f"Event: {event_msg} was not captured",
        )

    def assertEventNotCaptured(self, client, event_level, event_msg):
        self.assertFalse(
            client.transport.has_event(event_level, event_msg),
            msg=f"Event: {event_msg} was captured",
        )

    def test_initialize_raven_sets_dsn(self):
        self.assertEqual(self.client.dsn, self.dsn)

    def test_ignore_low_level_event(self):
        level, msg = logging.WARNING, "Test event, can be ignored"
        self.log(level, msg)
        level = "warning"
        self.assertEventNotCaptured(self.client, level, msg)

    def test_capture_event(self):
        level, msg = logging.ERROR, "Test event, should be captured"
        self.log(level, msg)
        level = "error"
        self.assertEventCaptured(self.client, level, msg)

    def test_capture_event_exc(self):
        level, msg = logging.ERROR, "Test event, can be ignored exception"
        try:
            raise TestException(msg)
        except TestException:
            exc_info = sys.exc_info()
        self.log(level, msg, exc_info)
        level = "error"
        self.assertEventCaptured(self.client, level, msg)

    def test_capture_events_no_tags(self):
        """Our 'before_send' can handle events without tags"""
        level, msg = logging.ERROR, "Test event, can be ignored exception"
        try:
            raise TestException(msg)
        except TestException:
            exc_info = sys.exc_info()
        self.log(level, msg, exc_info)
        level = "error"
        event = self.client.transport.has_event(level, msg)
        self.assertTrue(event)
        # Offer an event without tags to the before_send hook
        if "tags" in event:
            del event["tags"]
        self.assertTrue(before_send(event, {}))

    def test_ignore_exceptions(self):
        self.patch_config(
            {
                "sentry_ignore_exceptions": "odoo.exceptions.UserError",
            }
        )
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        client.transport = InMemoryTransport({"dsn": self.dsn})
        level, msg = logging.ERROR, "Test exception"
        try:
            raise exceptions.UserError(msg)
        except exceptions.UserError:
            exc_info = sys.exc_info()
        self.log(level, msg, exc_info)
        level = "error"
        self.assertEventNotCaptured(client, level, msg)

    def test_capture_exceptions_with_no_exc_info(self):
        """A UserError that isn't in the DEFAULT_IGNORED_EXCEPTIONS list is captured
        (there is no exc_info in the ValidationError exception)."""
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        client.transport = InMemoryTransport({"dsn": self.dsn})
        level, msg = logging.ERROR, "Test exception"

        # Odoo handles UserErrors by logging the exception
        with patch("odoo.addons.sentry.const.DEFAULT_IGNORED_EXCEPTIONS", new=[]):
            self.log(level, exceptions.ValidationError(msg))

        level = "error"
        self.assertEventCaptured(client, level, msg)

    def test_ignore_exceptions_with_no_exc_info(self):
        """A UserError that is in the DEFAULT_IGNORED_EXCEPTIONS is not captured
        (there is no exc_info in the ValidationError exception)."""
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        client.transport = InMemoryTransport({"dsn": self.dsn})
        level, msg = logging.ERROR, "Test exception"

        # Odoo handles UserErrors by logging the exception
        self.log(level, exceptions.ValidationError(msg))

        level = "error"
        self.assertEventNotCaptured(client, level, msg)

    def test_exclude_logger(self):
        self.patch_config(
            {
                "sentry_enabled": True,
                "sentry_exclude_loggers": self.logger.name,
            }
        )
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        client.transport = InMemoryTransport({"dsn": self.dsn})
        level, msg = logging.ERROR, f"Test exclude logger {__name__}"
        self.log(level, msg)
        level = "error"
        # Revert ignored logger so it doesn't affect other tests
        remove_handler_ignore(self.logger.name)
        self.assertEventNotCaptured(client, level, msg)

    def test_invalid_logging_level(self):
        self.patch_config(
            {
                "sentry_logging_level": "foo_bar",
            }
        )
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        client.transport = InMemoryTransport({"dsn": self.dsn})
        level, msg = logging.WARNING, "Test we use the default"
        self.log(level, msg)
        level = "warning"
        self.assertEventCaptured(client, level, msg)

    def test_undefined_to_int(self):
        self.assertIsNone(to_int_if_defined(""))

    def test_options_from_env_are_selected_by_prefix(self):
        """Only ODOO_SENTRY_* is ours, and it is renamed to the key the file uses."""
        environ = {
            "ODOO_SENTRY_DSN": self.dsn,
            "ODOO_SENTRY_TRACES_SAMPLE_RATE": "0.5",
            # sentry-sdk reads this one on its own, for whichever process it runs in
            "SENTRY_DSN": "http://public:secret@example.com/2",
            "ODOO_QUEUE_JOB_CHANNELS": "root:1",
        }
        self.assertEqual(
            get_options_from_env(environ),
            {"sentry_dsn": self.dsn, "sentry_traces_sample_rate": "0.5"},
        )

    def test_to_bool_reads_the_strings_a_config_source_delivers(self):
        for value in ("true", "True", "1", "on", "YES", True):
            self.assertTrue(to_bool(value), f"{value!r} should read as enabled")
        for value in ("false", "False", "0", "off", "no", False):
            self.assertFalse(to_bool(value), f"{value!r} should read as disabled")
        # Missing or left empty says nothing, so the caller's default answers.
        self.assertTrue(to_bool(None, default=True))
        self.assertTrue(to_bool("  ", default=True))
        self.assertFalse(to_bool(None))

    def test_configured_entirely_through_the_environment(self):
        """No configuration file at all: every option comes from the environment."""
        self.patch_env(
            {
                "ODOO_SENTRY_ENABLED": "true",
                "ODOO_SENTRY_DSN": self.dsn,
            }
        )
        client = initialize_sentry({})._client
        self.assertEqual(client.dsn, self.dsn)

    def test_environment_wins_over_the_configuration_file(self):
        env_dsn = "http://public:secret@example.com/2"
        self.patch_env({"ODOO_SENTRY_DSN": env_dsn})
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        self.assertEqual(client.dsn, env_dsn)

    def test_both_sources_are_merged_per_option(self):
        """An option set in only one of the two sources still reaches the client."""
        self.patch_env({"ODOO_SENTRY_ENVIRONMENT": "from-env"})
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        self.assertEqual(client.dsn, self.dsn, "the file should still be read")
        self.assertEqual(client.options["environment"], "from-env")

    def test_sentry_sdk_own_dsn_variable_is_not_read_as_ours(self):
        self.patch_env({"SENTRY_DSN": "http://public:secret@example.com/2"})
        client = initialize_sentry(sentry_hooks.sentry_config)._client
        self.assertEqual(client.dsn, self.dsn)

    def test_enabled_reads_the_string_false_as_off(self):
        self.patch_config({"sentry_enabled": "False"})
        self.assertIsNone(initialize_sentry(sentry_hooks.sentry_config))

    def test_enabled_from_the_environment_reads_the_string_false_as_off(self):
        self.patch_env({"ODOO_SENTRY_ENABLED": "False"})
        self.assertIsNone(initialize_sentry(sentry_hooks.sentry_config))

    @patch("odoo.addons.sentry.hooks.get_odoo_commit", return_value=GIT_SHA)
    def test_config_odoo_dir(self, get_odoo_commit):
        self.patch_config({"sentry_odoo_dir": "/opt/odoo/core"})
        client = initialize_sentry(sentry_hooks.sentry_config)._client

        self.assertEqual(
            client.options["release"],
            GIT_SHA,
            "Failed to use 'sentry_odoo_dir' parameter appropriately",
        )

    @patch("odoo.addons.sentry.hooks.get_odoo_commit", return_value=GIT_SHA)
    def test_config_release(self, get_odoo_commit):
        self.patch_config(
            {
                "sentry_odoo_dir": "/opt/odoo/core",
                "sentry_release": RELEASE,
            }
        )
        client = initialize_sentry(sentry_hooks.sentry_config)._client

        self.assertEqual(
            client.options["release"],
            RELEASE,
            "Failed to use 'sentry_release' parameter appropriately",
        )

    @patch("odoo.addons.sentry.hooks.sentry_sdk.capture_message")
    def test_sentry_startup_message_toggle(self, capture_message):
        self.patch_config({"sentry_startup_message": False})
        initialize_sentry(sentry_hooks.sentry_config)
        capture_message.assert_not_called()

        capture_message.reset_mock()
        self.patch_config({"sentry_startup_message": True})
        initialize_sentry(sentry_hooks.sentry_config)
        capture_message.assert_called_once_with("Starting Odoo Server", "info")

    def test_initialize_sentry_patches_application_call_when_server_missing(self):
        original_root = odoo.http.root
        original_application = odoo.http.Application

        class DummyRoot:
            def __init__(self):
                self.session_store = object()

        class DummyApplication:
            def __call__(self, environ, start_response):
                return "ok"

        try:
            dummy_root = DummyRoot()
            original_call = DummyApplication.__call__
            odoo.http.root = dummy_root
            odoo.http.Application = DummyApplication
            with (
                patch("odoo.addons.sentry.hooks.server", new=None),
                patch("odoo.addons.sentry.hooks._ORIGINAL_APPLICATION_CALL", new=None),
            ):
                initialize_sentry(sentry_hooks.sentry_config)
            self.assertTrue(inspect.isclass(odoo.http.Application))
            self.assertIs(odoo.http.root, dummy_root)
            self.assertTrue(hasattr(odoo.http.root, "session_store"))
            self.assertIs(odoo.http.root.session_store, dummy_root.session_store)
            self.assertIsNot(odoo.http.Application.__call__, original_call)
        finally:
            odoo.http.root = original_root
            odoo.http.Application = original_application

    def test_initialize_sentry_wraps_server_app_and_patches_application_call(self):
        original_root = odoo.http.root
        original_application = odoo.http.Application

        class DummyRoot:
            def __init__(self):
                self.session_store = object()

        class DummyApplication:
            def __call__(self, environ, start_response):
                return "ok"

        class DummyServer:
            def __init__(self):
                self.app = lambda environ, start_response: "server-ok"

        dummy_server = DummyServer()
        try:
            dummy_root = DummyRoot()
            original_call = DummyApplication.__call__
            odoo.http.root = dummy_root
            odoo.http.Application = DummyApplication
            with (
                patch("odoo.addons.sentry.hooks.server", new=dummy_server),
                patch("odoo.addons.sentry.hooks._ORIGINAL_APPLICATION_CALL", new=None),
            ):
                initialize_sentry(sentry_hooks.sentry_config)
            self.assertIsInstance(dummy_server.app, SentryWsgiMiddleware)
            self.assertTrue(inspect.isclass(odoo.http.Application))
            self.assertIs(odoo.http.root, dummy_root)
            self.assertTrue(hasattr(odoo.http.root, "session_store"))
            self.assertIs(odoo.http.root.session_store, dummy_root.session_store)
            self.assertIsNot(odoo.http.Application.__call__, original_call)
        finally:
            odoo.http.root = original_root
            odoo.http.Application = original_application
