# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import fields, models


class ImportOdooDatabaseField(models.Model):
    _name = 'import.odoo.database.field'
    _description = 'A field mapping for records in the remote database'

    database_id = fields.Many2one(
        'import.odoo.database', string='Database', required=True,
        ondelete='cascade',
    )
    model_id = fields.Many2one(
        'ir.model', string='Model', required=True, ondelete='cascade',
    )
    fields_id = fields.Many2one(
        'ir.model.fields', string='Field', help='If set, the mapping is only '
        'effective when setting said field', ondelete='cascade',
    )
    unique = fields.Boolean(
        'Unique', help='If set on a char field, a number is appended until '
        'the value is unique. Set this for fields with uniqueness constraints',
    )
    # TODO: create a reference function field to set this conveniently
    local_id = fields.Integer(
        'Local ID', help='If you leave this empty, a new record will be '
        'created in the local database when this field is set on the remote '
        'database'
    )
    remote_id = fields.Integer(
        'Remote ID', help='If you leave this empty, every (set) field value '
        'will be mapped to the local ID'
    )
