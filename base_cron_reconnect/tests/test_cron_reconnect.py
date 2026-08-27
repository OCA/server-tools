# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import os
import unittest
from unittest import mock

from odoo.tests.common import BaseCase

from .. import hooks


class TestCronReconnect(BaseCase):
    """No ORM/database needed: this module has no models, only a
    server_wide post_load hook that patches a class attribute. Using
    ``BaseCase`` rather than plain ``unittest.TestCase`` only for its
    ``MetaCase`` metaclass, which sets ``test_tags``/``test_module``/
    ``test_class``. Without those, Odoo's own test runner
    (``TagsSelector.check()``, odoo/tests/tag_selector.py) silently
    excludes every test in this class whenever it's invoked with
    tag-based filtering - including module-scoped filters like
    ``--test-tags=/base_cron_reconnect``, which OCA CI commonly uses.
    These tests still pass fine locally via plain
    ``python -m unittest``, which never applies Odoo's tag filter at
    all - that's what masked the gap during development.
    """

    def setUp(self):
        super().setUp()
        self._original_cron_thread = hooks.server.ThreadedServer.cron_thread
        self._original_on_stop_funcs = list(hooks.server.CommonServer._on_stop_funcs)
        hooks._stop_event.clear()
        self.addCleanup(self._restore)

    def _restore(self):
        hooks.server.ThreadedServer.cron_thread = self._original_cron_thread
        hooks.server.CommonServer._on_stop_funcs[:] = self._original_on_stop_funcs
        hooks._stop_event.clear()

    def test_crash_is_retried_not_propagated(self):
        """A cron_thread that raises is retried, not left dead."""
        calls = []

        def fake_cron_thread(self_, number):
            calls.append(number)
            if len(calls) < 3:
                raise ConnectionError("connection to server ... failed")
            # third call "succeeds": stop the supervisor loop cleanly.
            hooks._stop_event.set()

        hooks.server.ThreadedServer.cron_thread = fake_cron_thread

        # NOTE: pass the numeric logging.INFO, not the string "INFO".
        # odoo/netsvc.py does `logging.addLevelName(logging.RUNBOT, "INFO")`,
        # which hijacks the *name* "INFO" to mean level 25 process-wide.
        # assertLogs(level="INFO") would resolve the string through that
        # hijacked mapping and silently capture nothing from a plain
        # logger.info() call (level 20).
        with mock.patch.object(
            hooks._stop_event, "wait", return_value=False
        ) as wait_mock, self.assertLogs(hooks._logger.name, level=logging.INFO) as logs:
            hooks.post_load()
            hooks.server.ThreadedServer.cron_thread(None, 0)

        self.assertEqual(len(calls), 3)
        self.assertEqual(
            wait_mock.call_args_list,
            [
                mock.call(hooks.DEFAULT_RETRY_INTERVAL),
                mock.call(hooks.DEFAULT_RETRY_INTERVAL),
            ],
        )
        warning_records = [r for r in logs.records if r.levelname == "WARNING"]
        # post_load() itself logs one INFO confirmation line; filter it out
        # to isolate the "restarting now" records we actually care about.
        restart_records = [
            r for r in logs.records if "restarting now" in r.getMessage()
        ]
        self.assertEqual(len(warning_records), 2)
        for record in warning_records:
            self.assertIsNotNone(record.exc_info)
            self.assertIn("cron0", record.getMessage())
        # One "restarting now" per retry that actually happens (not logged
        # if a shutdown is what ends the wait instead - see the dedicated
        # test below).
        self.assertEqual(len(restart_records), 2)

    def test_no_restart_log_if_shutdown_wins_the_race(self):
        """No 'restarting now' log if _stop_event fires during the wait."""
        calls = []

        def fake_cron_thread(self_, number):
            calls.append(number)
            raise ConnectionError("connection to server ... failed")

        hooks.server.ThreadedServer.cron_thread = fake_cron_thread

        def wait_and_shutdown(timeout):
            # Simulate a clean server shutdown winning the race against
            # the retry wait: the event becomes set while we're "waiting".
            hooks._stop_event.set()
            return True

        with mock.patch.object(
            hooks._stop_event, "wait", side_effect=wait_and_shutdown
        ), self.assertLogs(hooks._logger.name, level=logging.INFO) as logs:
            hooks.post_load()
            hooks.server.ThreadedServer.cron_thread(None, 2)

        self.assertEqual(len(calls), 1)
        restart_records = [
            r for r in logs.records if "restarting now" in r.getMessage()
        ]
        stopped_records = [
            r for r in logs.records if "stopped gracefully" in r.getMessage()
        ]
        self.assertEqual(restart_records, [])
        self.assertEqual(len(stopped_records), 1)

    def test_lifecycle_logs_starting_and_stopped(self):
        """cronN logs 'starting' and 'stopped gracefully' at INFO level,
        matching queue_job's jobrunner lifecycle logging - Odoo's own
        cron_spawn()/cron_thread() only log the equivalent at DEBUG (start)
        or not at all (stop).
        """

        def fake_cron_thread(self_, number):
            hooks._stop_event.set()

        hooks.server.ThreadedServer.cron_thread = fake_cron_thread

        with self.assertLogs(hooks._logger.name, level=logging.INFO) as logs:
            hooks.post_load()
            hooks.server.ThreadedServer.cron_thread(None, 3)

        messages = [r.getMessage() for r in logs.records]
        self.assertIn("cron3 starting", messages)
        self.assertIn("cron3 stopped gracefully", messages)

    def test_post_load_is_idempotent(self):
        """Calling post_load() more than once must not double-wrap."""

        def sentinel(self_, number):
            pass

        hooks.server.ThreadedServer.cron_thread = sentinel

        hooks.post_load()
        patched = hooks.server.ThreadedServer.cron_thread
        self.assertIsNot(patched, sentinel)
        self.assertTrue(getattr(patched, hooks._PATCH_MARKER, False))

        on_stop_count = len(hooks.server.CommonServer._on_stop_funcs)

        hooks.post_load()
        hooks.post_load()

        self.assertIs(hooks.server.ThreadedServer.cron_thread, patched)
        self.assertEqual(len(hooks.server.CommonServer._on_stop_funcs), on_stop_count)

    def test_retry_interval_from_config(self):
        with mock.patch.dict(hooks.config.options, {hooks.CONFIG_KEY: "5"}):
            self.assertEqual(hooks._get_retry_interval(), 5)

        with mock.patch.dict(hooks.config.options, {hooks.CONFIG_KEY: "not-a-number"}):
            self.assertEqual(hooks._get_retry_interval(), hooks.DEFAULT_RETRY_INTERVAL)

        with mock.patch.dict(hooks.config.options, {hooks.CONFIG_KEY: "0"}):
            self.assertEqual(hooks._get_retry_interval(), 1)

        with mock.patch.dict(hooks.config.options, {}, clear=True):
            with mock.patch.dict(os.environ, {hooks.ENV_VAR: "7"}):
                self.assertEqual(hooks._get_retry_interval(), 7)


if __name__ == "__main__":
    unittest.main()
