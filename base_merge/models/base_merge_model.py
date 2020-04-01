# -*- coding: utf-8 -*-
# © 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


# This class holds configuration about which models
# are allowed to be merged, and which
# fields are to be used to to match
class BaseMergeModel(models.Model):

    _name = 'base.merge.model'

    _sql_constraints = [
        (
            'model_id_unique',
            'UNIQUE (model_id)',
            _('A record for this model already exists'),
        ),
    ]

    model_id = fields.Many2one(
        comodel_name='ir.model',
        string="Model",
        required=True)
    field_ids = fields.One2many(
        comodel_name='base.merge.model.line',
        inverse_name='merge_model_id')
    action_id = fields.Many2one(
        comodel_name='ir.actions.act_window')

    @api.multi
    def action_find_duplicates(self):
        """
        Use the fields defined in self to find the first set of duplicates,
        return an action that starts the merge wizard
        with the good context keys. This function can be used in
        server actions to start an interactive deduplication
        """
        return NotImplementedError(_('Currently not available'))

    @api.model
    def create(self, vals):
        # Create proper action and ir.values records
        # This enables merging for model_id
        record = super(BaseMergeModel, self).create(vals)
        record.action_id = self.env['ir.actions.act_window'].create({
            'name': 'Record merger',
            'type': 'ir.actions.act_window',
            'res_model': 'base.merge.wizard',
            'src_model': record.model_id.model,
            'view_mode': 'form',
            'target': 'new',
        })
        self.env['ir.values'].set_action(
            _('Merge action for %s') % record.model_id.model,
            'client_action_multi',
            record.model_id.model,
            '%s, %d' % (record.action_id.type, record.action_id.id))
        return record

    @api.multi
    def unlink(self):
        value_model = self.env['ir.values']
        for this in self:
            # Unlink ir.values
            value_model.search([
                ('action_id', '=', this.action_id.id),
                ('model_id', '=', this.model_id.id),
            ]).unlink()
            # Unlink the action
            this.action_id.unlink()
        # Unlink in general
        return super(BaseMergeModel, self).unlink()

    @api.multi
    def name_get(self):
        return [(
            merger_record.id,
            'Merging enabled for %s' % (
                merger_record.model_id.name or '',
            )) for merger_record in self]
