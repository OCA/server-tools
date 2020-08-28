# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright (c) ACSONE SA/NV 2019

import logging
import os
import time

import psycopg2

from odoo import sql_db
from odoo.tools import config

_logger = logging.getLogger(__name__)

# TODO Odoo option? server_environment?
LOG_MIN_DURATION_STATEMENT = int(config.get("log_min_duration_statement", "-1"))
ENV_VAR = "ODOO_LOG_MIN_DURATION_STATEMENT"
if ENV_VAR in os.environ:
    LOG_MIN_DURATION_STATEMENT = int(os.environ.get(ENV_VAR, "-1"))


class SlowStatementLoggingCursor(sql_db.Cursor):
    def execute(self, query, params=None, log_exceptions=None):
        if LOG_MIN_DURATION_STATEMENT >= 0:
            start = time.perf_counter()
            res = super().execute(query, params, log_exceptions)
            duration = (time.perf_counter() - start) * 1000.0
            if duration >= LOG_MIN_DURATION_STATEMENT:
                # same logging technique as Odoo in sql_log mode
                encoding = psycopg2.extensions.encodings[self.connection.encoding]
                _logger.debug(
                    "duration: %.3f ms  statement: %s",
                    duration,
                    self._obj.mogrify(query, params).decode(encoding, "replace"),
                )
            return res
        else:
            return super().execute(query, params, log_exceptions)


sql_db.Cursor = SlowStatementLoggingCursor
