# Copyright 2026 Vauxoo <https://www.vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import threading

import odoo.service.server
import odoo.sql_db
from odoo.tools import config

_logger = logging.getLogger(__name__)

# Cron workers/threads keep a long-lived "LISTEN cron_trigger" connection
# to the "postgres" database, which is not compatible with PgBouncer in
# transaction pooling mode (same limitation as the bus dispatcher).
#
# There is no hook to alter only that connection: both entry points call
# ``sql_db.db_connect("postgres")`` directly. So we flag the cron threads
# (and the cron worker processes) and redirect their connections to the
# "postgres" database to the alternate host/port.
_cron_context = threading.local()


def _cron_db_config(param):
    """Return the alternate connection parameter for cron connections.

    Falls back to the imdispatcher (bus) settings, so a single
    configuration can redirect both LISTEN/NOTIFY connections.
    """
    return (
        os.environ.get(f"ODOO_CRON_DB_{param.upper()}")
        or config.get("cron_db_" + param)
        or os.environ.get(f"ODOO_IMDISPATCHER_DB_{param.upper()}")
        or config.get("imdispatcher_db_" + param)
    )


_orig_connection_info_for = odoo.sql_db.connection_info_for


def connection_info_for(db_or_uri, *args, **kwargs):
    db_name, connection_info = _orig_connection_info_for(db_or_uri, *args, **kwargs)
    if db_or_uri == "postgres" and getattr(_cron_context, "redirect", False):
        for p in ("host", "port"):
            cfg = _cron_db_config(p)
            if cfg:
                connection_info[p] = cfg
        _logger.debug(
            "Cron connection to db postgres via %s:%s",
            connection_info.get("host"),
            connection_info.get("port"),
        )
    return db_name, connection_info


_orig_worker_cron_start = odoo.service.server.WorkerCron.start


def _worker_cron_start(self):
    _cron_context.redirect = True
    return _orig_worker_cron_start(self)


_orig_cron_thread = odoo.service.server.ThreadedServer.cron_thread


def _cron_thread(self, number):
    _cron_context.redirect = True
    return _orig_cron_thread(self, number)


odoo.sql_db.connection_info_for = connection_info_for
odoo.service.server.WorkerCron.start = _worker_cron_start
odoo.service.server.ThreadedServer.cron_thread = _cron_thread

if _cron_db_config("host") or _cron_db_config("port"):
    _logger.info(
        "Cron LISTEN connections will be redirected via %s:%s",
        _cron_db_config("host") or config.get("db_host") or "<default>",
        _cron_db_config("port") or config.get("db_port") or "<default>",
    )
