# Copyright 2019 Trobz <https://trobz.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os
import json
import logging
import select

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import odoo
from odoo import api, models
from odoo.tools import config

from odoo.addons.bus.models.bus import hashable, json_dump, TIMEOUT
import odoo.addons.bus.models.bus


_logger = logging.getLogger(__name__)


def _connection_info():
    database = os.environ.get(
        'ODOO_IMDISPATCHER_DB_NAME',
        config.get('imdispatcher_db_name')
        ) or 'postgres'

    db_or_uri, connection_info = odoo.sql_db.connection_info_for(database)

    for p in ('host', 'port'):
        cfg = (os.environ.get('ODOO_IMDISPATCHER_DB_%s' % p.upper()) or
               config.get('imdispatcher_db_' + p))

        if cfg:
            connection_info[p] = cfg

    return connection_info


class ImBus(models.Model):

    _inherit = 'bus.bus'

    @api.model
    def sendmany(self, notifications):
        channels = set()
        for channel, message in notifications:
            channels.add(channel)
            values = {
                "channel": json_dump(channel),
                "message": json_dump(message)
            }
            self.sudo().create(values)
        if channels:
            # We have to wait until the notifications are commited in database.
            # When calling `NOTIFY imbus`, some concurrent threads will be
            # awakened and will fetch the notification in the bus table. If the
            # transaction is not commited yet, there will be nothing to fetch,
            # and the longpolling will return no notification.
            def notify():
                database = _connection_info()["database"]
                _, connection_info = odoo.sql_db.connection_info_for(database)
                _logger.debug("Bus.sendmany to db %(database)s "
                              "(via %(host)s:%(port)s)",
                              connection_info)
                with odoo.sql_db.db_connect(database).cursor() as cr:
                    cr.execute("notify imbus, %s", (json_dump(list(channels)),))
            self._cr.after('commit', notify)


class ImDispatch(odoo.addons.bus.models.bus.ImDispatch):

    def loop(self):
        """ Dispatch postgres notifications to the relevant
            polling threads/greenlets """
        connection_info = _connection_info()
        _logger.info("Bus.loop listen imbus on db %(database)s "
                     "(via %(host)s:%(port)s)",
                     connection_info)
        conn = psycopg2.connect(**connection_info)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cr:
            cr.execute("listen imbus")
            conn.commit()
            while True:
                if select.select([conn], [], [], TIMEOUT) == ([], [], []):
                    pass
                else:
                    conn.poll()
                    channels = []
                    while conn.notifies:
                        channels.extend(json.loads(conn
                                                   .notifies.pop().payload))
                    # dispatch to local threads/greenlets
                    events = set()
                    for channel in channels:
                        events.update(self.channels.pop(hashable(channel),
                                                        set()))
                    for event in events:
                        event.set()


odoo.addons.bus.models.bus.ImDispatch = ImDispatch

# we can replace the existing dispatcher because its thread
# has not been started yet; indeed, since a2ed3d it only starts
# on first /poll request:
# https://github.com/odoo/odoo/commit/a2ed3d3d5bdb6025a1ba14ad557a115a86413e65

if not odoo.multi_process or odoo.evented:
    dispatch = ImDispatch()
    odoo.addons.bus.models.bus.dispatch = dispatch
    odoo.addons.bus.controllers.main.dispatch = dispatch
