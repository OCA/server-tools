# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from ..identifier_adapter import IdentifierAdapter


DB_FIELD_TYPES = [
    'binary',
    'boolean',
    'char',
    'date',
    'datetime',
    'float',
    'html',
    'integer',
    'many2one',
    'monetary',
    'reference',
    'selection',
    'text',
    ]

MODULE_UNINSTALL_FLAG = '_force_unlink'
FIELD_TYPES = [(key, key) for key in sorted(fields.Field.by_type)]


class CleanupPurgeLineModelField(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.model.field'
    _description = 'Purge Fields Wizard Lines'

    field_id = fields.Many2one(
        'ir.model.fields',
        'Field',
        required=True,
        ondelete='CASCADE'
        )
    model_id = fields.Many2one(
        related='field_id.model_id',
        store=True
        )
    ttype = fields.Selection(
        related='field_id.ttype',
        selection=FIELD_TYPES,
        string='Field Type')
    table = fields.Char(
        compute='_compute_table_name',
        string='Table',
        store=True,
        readonly=True
        )
    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.model.field',
        'Purge Wizard',
        readonly=True
        )

    @api.multi
    def purge(self):
        for line in self:
            # We pass MODULE_UNINSTALL_FLAG to be able to remove fields as by default
            # only module uninstallation can remove fields that contain data
            line.field_id.with_context({MODULE_UNINSTALL_FLAG: True}).unlink()

    @api.depends('model_id')
    def _compute_table_name(self):
        for rec in self:
            rec.table = self.env[rec.field_id.model]._table


class CleanupPurgeWizardModelField(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.model.field'
    _description = 'Purge Fields'

    @api.model
    def find(self):
        """
        Search for ir.model.fields that are stored and do not exist in tables.
        """
        res = []

        stored_fields = self.env['ir.model.fields'].search([
            ('ttype', 'in', DB_FIELD_TYPES),
            ('store', '=', True),
            ])

        for field in stored_fields:
            self.env.cr.execute(
                '''SELECT table_name, column_name
                FROM information_schema."columns" c
                WHERE table_schema = 'public'
                AND table_name = %s
                AND column_name = %s;
                ''',
                (self.env[field.model]._table, field.name))
            columns = self.env.cr.fetchall()

            if not columns:
                if not self.env[field.model]._abstract:
                    if not field.name in self.env[field.model]._fields:
                        res.append((0, 0, {
                            'name': field.name,
                            'field_id': field.id}))
                        continue
                    if field.ttype == 'binary':
                        if not self.env[field.model]._fields[field.name].attachment:
                            res.append((0, 0, {
                                'name': field.name,
                                'field_id': field.id}))
                        continue
                    if not field.modules and not field.name[:2] == 'x_':
                        res.append((0, 0, {
                            'name': field.name,
                            'field_id': field.id}))

        if not res:
            raise UserError(_('No orphaned fields found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.model.field', 'wizard_id', 'Fields to purge')
