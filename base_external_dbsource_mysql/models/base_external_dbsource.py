# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# Copyright 2017 Henry Zhou <zhouhenry@live.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base_external_dbsource.models import (
        base_external_dbsource,
    )
    CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
        CONNECTORS.append(('mysql', 'MySQL'))
        assert pymysql
    except (ImportError, AssertionError):
        _logger.info('MySQL not available. Please install "pymysql" '
                     'python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to a MySQL data source. """

    _inherit = "base.external.dbsource"

    @api.multi
    def connection_close_mysql(self, connection):
        return connection.close()

    @api.multi
    def connection_open_mysql(self):
        return self._connection_open_sqlalchemy()

    @api.multi
    def execute_mysql(self, sqlquery, sqlparams, metadata):
        return self._execute_sqlalchemy(sqlquery, sqlparams, metadata)
