# Copyright 2019 Trobz <https://trobz.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import time
from datetime import datetime

from odoo import http
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, config

_logger = logging.getLogger(__name__)


old_session_gc = http.session_gc


def session_gc(session_store):
    return


def deterministic_session_gc(session_store, session_expiry_delay=None):
    if session_expiry_delay is None:
        session_expiry_delay = config.get("session_expiry_delay", 60 * 60 * 24 * 7)
    expired_time = time.time() - int(session_expiry_delay)
    _logger.debug(
        "Deleting all sessions inactive since %s",
        datetime.fromtimestamp(expired_time).strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    )
    for fname in os.listdir(session_store.path):
        path = os.path.join(session_store.path, fname)
        try:
            if os.path.getmtime(path) < expired_time:
                os.unlink(path)
        except OSError as e:
            _logger.debug(e)


if "base_deterministic_session_gc" in config.get("server_wide_modules"):
    _logger.debug("Disabling default session_gc")
    http.session_gc = session_gc
    http.deterministic_session_gc = deterministic_session_gc
