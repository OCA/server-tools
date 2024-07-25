# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class IrModelData(models.Model):
    _inherit = 'ir.model.data'

    import_database_id = fields.Many2one(
        'import.odoo.database', string='From remote database',
    )
    import_database_record_id = fields.Integer('Remote database ID')
