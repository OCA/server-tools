# Copyright 2026 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
"""Restart threaded-mode (``workers = 0``) cron workers that die on a lost
database connection, instead of leaving them dead until the next restart.

``ThreadedServer.cron_thread`` has no exception handling around its
polling loop - unlike ``ir_cron._process_jobs()`` (job-level failures)
or ``PreforkServer`` (which respawns a crashed ``WorkerCron`` process).
This wraps ``cron_thread`` in the same catch-log-sleep-retry pattern
Odoo's own ``bus.ImDispatch.run()`` already uses for an equivalent
long-lived connection. No-op under prefork mode.

Full writeup: ``readme/DESCRIPTION.rst``. Related upstream reports -
core has taken a position that automatic recovery isn't in scope for
``ThreadedServer`` (see #88984): odoo/odoo#15666, #88984, #184421,
#215164.
"""
import logging
import os
import threading

from odoo.service import server
from odoo.tools import config

_logger = logging.getLogger(__name__)

#: Fallback retry interval (seconds) if neither the ``cron_reconnect_retry_interval``
#: ini option nor the ``ODOO_CRON_RECONNECT_RETRY_INTERVAL`` environment variable is
#: set. Matches ``odoo.service.server.SLEEP_INTERVAL``.
DEFAULT_RETRY_INTERVAL = 60
CONFIG_KEY = "cron_reconnect_retry_interval"
ENV_VAR = "ODOO_CRON_RECONNECT_RETRY_INTERVAL"

_PATCH_MARKER = "_cron_reconnect_patched"

#: Set once the server starts shutting down, so the wrapper can tell a
#: shutdown-induced crash (expected, quiet) from a real one (logged and
#: retried).
_stop_event = threading.Event()


def _get_retry_interval():
    """Return the configured retry interval, defaulting defensively."""
    raw = config.get(CONFIG_KEY) or os.environ.get(ENV_VAR)
    if raw is None:
        return DEFAULT_RETRY_INTERVAL
    try:
        value = int(raw)
    except (TypeError, ValueError):
        _logger.warning(
            "Invalid %s/%s value %r, falling back to %ss.",
            CONFIG_KEY,
            ENV_VAR,
            raw,
            DEFAULT_RETRY_INTERVAL,
        )
        return DEFAULT_RETRY_INTERVAL
    return max(1, value)


def post_load():
    """Patch ``ThreadedServer.cron_thread`` for auto-reconnect resilience.

    Safe to call more than once (idempotent) and safe to run under prefork
    mode (no-op there, since ``ThreadedServer`` is never used).
    """
    if getattr(server.ThreadedServer.cron_thread, _PATCH_MARKER, False):
        return

    original_cron_thread = server.ThreadedServer.cron_thread
    retry_interval = _get_retry_interval()

    # Make the wrapper below stop retrying as soon as the server starts a
    # clean shutdown, instead of logging a false-alarm WARNING on every
    # restart (``ThreadedServer.stop()`` closes all database connections
    # right after running the on-stop hooks, which reliably makes the
    # underlying cron_thread call raise).
    server.CommonServer.on_stop(_stop_event.set)

    def cron_thread(self, number):
        # original_cron_thread() never returns under normal operation (its
        # own inner loop is `while True:`, with no break/return) - it can
        # only ever exit by raising. So the only case to handle here is an
        # exception; a clean return is not a real possibility today.
        #
        # Odoo logs cron start/poll only at DEBUG (invisible by default)
        # and nothing at all on stop. Log the lifecycle at INFO instead,
        # matching queue_job's jobrunner ("starting"/"graceful stop
        # requested"/"stopped").
        _logger.info("cron%d starting", number)
        while not _stop_event.is_set():
            try:
                original_cron_thread(self, number)
            except Exception:
                if _stop_event.is_set():
                    break
                _logger.warning(
                    "cron%d died, most likely due to a lost database "
                    "connection; restarting it in %ss.",
                    number,
                    retry_interval,
                    exc_info=True,
                )
                _stop_event.wait(retry_interval)
                if not _stop_event.is_set():
                    _logger.info("cron%d restarting now.", number)
        _logger.info("cron%d stopped gracefully", number)

    setattr(cron_thread, _PATCH_MARKER, True)
    server.ThreadedServer.cron_thread = cron_thread
    _logger.info(
        "base_cron_reconnect: patched ThreadedServer.cron_thread to survive "
        "a lost database connection (retry interval: %ss).",
        retry_interval,
    )
