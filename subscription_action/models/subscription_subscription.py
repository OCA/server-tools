# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class SubscriptionSubscription(models.Model):
    _inherit = 'subscription.subscription'

    server_action_id = fields.Many2one(
        'ir.actions.server', string='Run action',
        help='If you need to run multiple actions, use an umbrella action',
    )
    model_id = fields.Many2one('ir.model', compute='_compute_model_id')

    @api.multi
    def model_copy(self):
        old_history = self.env['subscription.subscription.history'].search([
            ('subscription_id', 'in', self.ids),
        ])
        result = super(SubscriptionSubscription, self).model_copy()
        new_history = self.env['subscription.subscription.history'].search([
            ('subscription_id', 'in', self.ids),
        ])
        for history_item in new_history - old_history:
            action = history_item.subscription_id.server_action_id
            record = history_item.document_id
            if not action:
                continue
            action.with_context(
                active_id=record.id, active_ids=record.ids,
                active_model=record._name,
            ).run()
        return result

    @api.multi
    @api.depends('doc_source')
    def _compute_model_id(self):
        for this in self:
            if not this.doc_source:
                continue
            this.model_id = self.env['ir.model'].search([
                ('model', '=', this.doc_source._name),
            ], limit=1)
