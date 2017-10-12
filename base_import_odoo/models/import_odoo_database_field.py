# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ImportOdooDatabaseField(models.Model):
    _name = 'import.odoo.database.field'
    _description = 'A field mapping for records in the remote database'
    _order = 'database_id, sequence'

    sequence = fields.Integer()
    database_id = fields.Many2one(
        'import.odoo.database', string='Database', required=True,
        ondelete='cascade',
    )
    model_id = fields.Many2one(
        'ir.model', string='Model', required=True, ondelete='cascade',
    )
    model = fields.Char(related=['model_id', 'model'])
    field_ids = fields.Many2many(
        'ir.model.fields', string='Field', help='If set, the mapping is only '
        'effective when setting said field', ondelete='cascade',
    )
    model_field_id = fields.Many2one(
        'ir.model.fields', string='Model field', compute=lambda self:
        self._compute_reference_field('model_field_id', 'char'),
        inverse=lambda self:
        self._inverse_reference_field('model_field_id', 'char'),
    )
    id_field_id = fields.Many2one(
        'ir.model.fields', string='ID field', compute=lambda self:
        self._compute_reference_field('id_field_id', 'integer'),
        inverse=lambda self:
        self._inverse_reference_field('id_field_id', 'integer'),
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
    mapping_type = fields.Selection(
        [
            ('fixed', 'Fixed'),
            ('by_field', 'Based on equal fields'),
            ('by_reference', 'By reference'),
            ('unique', 'Unique'),
        ],
        string='Type', required=True, default='fixed',
    )

    @api.multi
    def _compute_reference_field(self, field_name, ttype):
        for this in self:
            this[field_name] = this.field_ids.filtered(
                lambda x: x.ttype == ttype
            )

    @api.multi
    def _inverse_reference_field(self, field_name, ttype):
        self.field_ids = self.field_ids.filtered(
            lambda x: x.ttype != ttype
        ) + self[field_name]
