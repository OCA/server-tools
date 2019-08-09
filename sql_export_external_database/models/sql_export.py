# -*- coding: utf-8 -*-
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from openerp import models, fields, api
from ..sql_db import get_external_cursor


class SqlExport(models.Model):
    _inherit = "sql.export"

    use_external_database = fields.Boolean(
        help=("If filled, the query will be executed against an external "
              "database, configured in Odoo main configuration file. "))

    @api.multi
    def _get_cr_for_query(self):
        if self.use_external_database:
            external_db_cr = get_external_cursor()
            return external_db_cr
        return super(SqlExport, self)._get_cr_for_query()

    @api.model
    def _rollback_savepoint(self, rollback_name, cr):
        res = super(SqlExport, self)._rollback_savepoint(rollback_name, cr)
        if self.env.cr != cr:
            cr.close()
        return res
