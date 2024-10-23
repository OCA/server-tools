# Copyright 2019 Trobz <https://trobz.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
import os
import selectors

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import odoo
from odoo.tools import config

import odoo.addons.bus.models.bus
from odoo.addons.bus.models.bus import TIMEOUT, hashable, stop_event

_logger = logging.getLogger(__name__)


def _connection_info_for(db_name):
    db_or_uri, connection_info = odoo.sql_db.connection_info_for(db_name)

    for p in ("host", "port"):
        cfg = os.environ.get("ODOO_IMDISPATCHER_DB_%s" % p.upper()) or config.get(
            "imdispatcher_db_" + p
        )

        if cfg:
            connection_info[p] = cfg

    return connection_info


class ImDispatch(odoo.addons.bus.models.bus.ImDispatch):
    def loop(self):
        """Dispatch postgres notifications to the relevant
        polling threads/greenlets"""
        connection_info = _connection_info_for("postgres")
        _logger.info(
            "Bus.loop listen imbus on db postgres " "(via %(host)s:%(port)s)",
            connection_info,
        )
        conn = psycopg2.connect(**connection_info)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cr, selectors.DefaultSelector() as sel:
            cr.execute("listen imbus")
            conn.commit()
            while not stop_event.is_set():
                if sel.select(TIMEOUT):
                    conn.poll()
                    channels = []
                    while conn.notifies:
                        channels.extend(json.loads(conn.notifies.pop().payload))
                    # relay notifications to websockets that have
                    # subscribed to the corresponding channels.
                    websockets = set()
                    for channel in channels:
                        websockets.update(
                            self._channels_to_ws.get(hashable(channel), [])
                        )
                    for websocket in websockets:
                        websocket.trigger_notification_dispatching()


odoo.addons.bus.models.bus.ImDispatch = ImDispatch

# we can replace the existing dispatcher because its thread
# has not been started yet; indeed, since a2ed3d it only starts
# on first /poll request:
# https://github.com/odoo/odoo/commit/a2ed3d3d5bdb6025a1ba14ad557a115a86413e65

if not odoo.multi_process or odoo.evented:
    dispatch = ImDispatch()
    odoo.addons.bus.models.bus.dispatch = dispatch
    odoo.addons.bus.controllers.main.dispatch = dispatch
