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
        import pymssql
        CONNECTORS.append(('mssql', 'Microsoft SQL Server'))
        assert pymssql
    except (ImportError, AssertionError):
        _logger.info('MS SQL Server not available. Please install "pymssql" '
                     'python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to a MSSQL data source. """

    _inherit = "base.external.dbsource"

    PWD_STRING_MSSQL = 'Password=%s;'

    @api.multi
    def connection_close_mssql(self, connection):
        return connection.close()

    @api.multi
    def connection_open_mssql(self):
        return self._connection_open_sqlalchemy()

    @api.multi
    def execute_mssql(self, sqlquery, sqlparams, metadata):
        return self._execute_sqlalchemy(sqlquery, sqlparams, metadata)
