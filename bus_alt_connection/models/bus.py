# Copyright 2019 Trobz <https://trobz.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import os
import selectors
from collections import defaultdict

import psycopg2

import odoo
from odoo.tools import config

import odoo.addons.bus.bus_dispatcher
import odoo.addons.bus.models.ir_websocket
import odoo.addons.bus.websocket
from odoo.addons.bus.bus_dispatcher import (
    POLL_TIMEOUT,
    BusDispatcher,
    DispatchState,
    stop_event,
)
from odoo.addons.bus.tools import orjson
from odoo.addons.bus.tools.misc import tuplify

_logger = logging.getLogger(__name__)


def _connection_info_for(db_name):
    _db_or_uri, connection_info = odoo.sql_db.connection_info_for(db_name)

    for p in ("host", "port"):
        cfg = os.environ.get(f"ODOO_IMDISPATCHER_DB_{p.upper()}") or config.get(
            "imdispatcher_db_" + p
        )
        if cfg:
            connection_info[p] = cfg
    return connection_info


class AltConnectionBusDispatcher(BusDispatcher):
    """Listen for `imbus` notifications on a direct database connection.

    Core opens the listening cursor through `odoo.sql_db.db_connect`, which
    goes through the connection pooler. A pooler in transaction mode never
    delivers the asynchronous notifications a `LISTEN` relies on, so the body
    of `_listener_loop` is mirrored here with a plain psycopg2 connection built
    from `imdispatcher_db_host` / `imdispatcher_db_port`. Everything else,
    including the whole dispatch flow, is left to core.
    """

    def _listener_loop(self):
        db_system = config["db_system"]
        connection_info = _connection_info_for(db_system)
        _logger.info(
            "Bus._listener_loop listen imbus on db %s (via %s:%s)",
            db_system,
            connection_info.get("host"),
            connection_info.get("port"),
        )
        conn = psycopg2.connect(**connection_info)
        try:
            with conn.cursor() as cr, selectors.DefaultSelector() as sel:
                cr.execute("listen imbus")
                conn.commit()
                sel.register(conn, selectors.EVENT_READ)
                while not stop_event.is_set():
                    if not sel.select(POLL_TIMEOUT):
                        continue
                    conn.poll()
                    channels_by_dbname = defaultdict(list)
                    while conn.notifies:
                        for channel in orjson.loads(conn.notifies.pop().payload):
                            try:
                                channels_by_dbname[channel[0]].append(tuplify(channel))
                            except (IndexError, TypeError):
                                # Protect against malformed channels.
                                _logger.debug(
                                    "Discarding malformed bus channel %s", channel
                                )
                    for dbname, channels in channels_by_dbname.items():
                        with self._lock_for_db(dbname):
                            for channel in channels:
                                topic = self._topic_by_channel.get(channel)
                                if topic is None:
                                    continue
                                if topic._state is DispatchState.IDLE:
                                    self._queue_topic(topic)
                                elif topic._state is DispatchState.IN_FLIGHT:
                                    topic._state = DispatchState.DIRTY
                                # DIRTY and QUEUED: stay in that state.
        finally:
            conn.close()


dispatch = AltConnectionBusDispatcher()
odoo.addons.bus.bus_dispatcher.dispatch = dispatch
odoo.addons.bus.models.ir_websocket.dispatch = dispatch
odoo.addons.bus.websocket.dispatch = dispatch
