# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base_external_dbsource.models import (
        base_external_dbsource,
    )
    CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS
    try:
        import pyodbc
        CONNECTORS.append(('pyodbc', 'ODBC'))
    except ImportError:
        _logger.info('ODBC libraries not available. Please install '
                     '"unixodbc" and "python-pyodbc" packages.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to a ODBC data source. """

    _inherit = "base.external.dbsource"

    @api.multi
    def connection_close_pyodbc(self, connection):
        return connection.close()

    @api.multi
    def connection_open_pyodbc(self):
        return pyodbc.connect(self.conn_string_full)

    @api.multi
    def execute_pyodbc(self, sqlquery, sqlparams, metadata):
        return self._execute_generic(sqlquery, sqlparams, metadata)
