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
        import sqlalchemy
        CONNECTORS.append(('sqlite', 'SQLite'))
    except ImportError:
        _logger.info('SQLAlchemy library not available. Please '
                     'install "sqlalchemy" python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to a SQLite data source. """

    _inherit = "base.external.dbsource"

    PWD_STRING_SQLITE = 'Password=%s;'

    @api.multi
    def connection_close_sqlite(self, connection):
        return connection.close()

    @api.multi
    def connection_open_sqlite(self):
        return self._connection_open_sqlalchemy()

    @api.multi
    def execute_sqlite(self, sqlquery, sqlparams, metadata):
        return self._execute_sqlalchemy(sqlquery, sqlparams, metadata)

    @api.multi
    def _connection_open_sqlalchemy(self):
        return sqlalchemy.create_engine(self.conn_string_full).connect()

    @api.multi
    def _execute_sqlalchemy(self, sqlquery, sqlparams, metadata):
        rows, cols = list(), list()
        for record in self:
            with record.connection_open() as connection:
                cur = connection.execute(sqlquery, sqlparams)
                if metadata:
                    cols = cur.keys()
                rows = [r for r in cur]
        return rows, cols
