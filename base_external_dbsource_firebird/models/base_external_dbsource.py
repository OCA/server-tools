# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from openerp import api, models

_logger = logging.getLogger(__name__)

try:
    from openerp.addons.base_external_dbsource.models import (
        base_external_dbsource,
    )
    CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS
    try:
        import fdb
        CONNECTORS.append(('fdb', 'Firebird'))
    except:
        _logger.info('Firebird library not available. Please install "fdb" '
                     'python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to a Firebird data source. """

    _inherit = "base.external.dbsource"

    PWD_STRING_FDB = 'Password=%s;'

    @api.multi
    def connection_close_fdb(self, connection):
        return connection.close()

    @api.multi
    def connection_open_fdb(self):
        kwargs = {}
        for option in self.conn_string_full.split(';'):
            try:
                key, value = option.split('=')
            except ValueError:
                continue
            kwargs[key.lower()] = value
        return fdb.connect(**kwargs)

    @api.multi
    def execute_fdb(self, sqlquery, sqlparams, metadata):
        with self.connection_open_fdb() as conn:
            cur = conn.cursor()
            cur.execute(sqlquery % sqlparams)
            rows = cur.fetchall()
            return rows, []
