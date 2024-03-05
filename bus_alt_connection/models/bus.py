# Copyright 2019 Trobz <https://trobz.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
import logging
import os
import selectors

import psycopg2

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
        with conn.cursor() as cr, selectors.DefaultSelector() as sel:
            cr.execute("listen imbus")
            conn.commit()
            sel.register(conn, selectors.EVENT_READ)
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
dispatch = ImDispatch()
odoo.addons.bus.models.bus.dispatch = dispatch
odoo.addons.bus.models.ir_websocket.dispatch = dispatch
odoo.addons.bus.websocket.dispatch = dispatch
