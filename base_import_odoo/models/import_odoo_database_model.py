# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ImportOdooDatabaseModel(models.Model):
    _name = 'import.odoo.database.model'
    _description = 'A model to import from a remote database'
    _order = 'sequence'

    sequence = fields.Integer()
    model_id = fields.Many2one(
        'ir.model', string='Model', required=True, ondelete='cascade',
    )
    database_id = fields.Many2one(
        'import.odoo.database', string='Database', required=True,
        ondelete='cascade',
    )
    domain = fields.Char(help='Optional filter to import only a subset')
