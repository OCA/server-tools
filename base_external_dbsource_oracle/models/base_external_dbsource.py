# -*- coding: utf-8 -*-
# Copyright 2011 Daniel Reis
# Copyright 2016 LasLabs Inc.
# Copyright 2017 Henry Zhou <zhouhenry@live.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import logging
import os

from odoo import api
from odoo import models

_logger = logging.getLogger(__name__)

try:
    from odoo.addons.base_external_dbsource.models import (
        base_external_dbsource,
    )
    CONNECTORS = base_external_dbsource.BaseExternalDbsource.CONNECTORS
    try:
        import cx_Oracle
        CONNECTORS.append(('cx_Oracle', 'Oracle'))
    except ImportError:
        _logger.info('Oracle libraries not available. Please install '
                     '"cx_Oracle" python package.')
except ImportError:
    _logger.info('base_external_dbsource Odoo module not found.')


class BaseExternalDbsource(models.Model):
    """ It provides logic for connection to an Oracle data source. """

    _inherit = "base.external.dbsource"

    PWD_STRING_CX_ORACLE = 'Password=%s;'

    @api.multi
    def connection_close_cx_Oracle(self, connection):
        return connection.close()

    @api.multi
    def connection_open_cx_Oracle(self):
        os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.UTF8'
        return cx_Oracle.connect(self.conn_string_full)

    @api.multi
    def execute_cx_Oracle(self, sqlquery, sqlparams, metadata):
        return self._execute_generic(sqlquery, sqlparams, metadata)
