# -*- coding: utf-8 -*-
# © 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models


# this class holds configuration about which models are allowed to be merged, and which
# fields are to be used to to match
class BaseMergeModel(models.Model):
    
    _name = 'base.merge.model'

    model_id = fields.Many2one(
        comodel_name='ir.model',
        required=True)
    field_ids = fields.One2many(
        comodel_name='base.merge.model.line',
        inverse_name='merge_model_id')
    action_id = fields.Many2one(
        comodel_name='ir.actions.act_window')
    
    @api.multi
    def action_create_action(self):
        ''' 
        Create a multi window action for the model in model_id to start our
        base.merge.wizard that does the actual work. Write the action in action_id
        '''
        # Create the action
        self.action_id = self.env['ir.actions.act_window'].create({
            'name': 'Record merger',
            'type': 'ir.actions.act_window',
            'res_model': 'base.merge.wizard',
            'src_model': self.model_id.model,
            'view_mode': 'form',
            'target': 'new',
        })
        # create ir.values
        return self.env['ir.values'].set_action(
            _('Merge action for %s') % self.model_id.model,
            'client_action_multi',
            self.model_id.model,
            '%s, %d' % (self.action_id.type, self.action_id.id))

    def action_delete_action(self):
        return self.mapped('action_id').unlink()
    
    @api.multi
    def action_find_duplicates(self):
        return
      # use the fields defined in self to find the first set of duplicates, return
      # an action that starts the merge wizard with the good context keys.
      # this function can be used in server actions to start an interactive deduplication
