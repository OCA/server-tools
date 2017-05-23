# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import models, fields, api, _
import logging

class AuditlogRule(models.Model):
    _inherit = 'auditlog.rule'
    _logger = logging.getLogger(__name__)

    @api.model
    def set_subscription_state(self, state='subscribed'):
        active_ids = self.env.context.get('active_ids', -1)
        active_rules = self.search([('id', 'in', active_ids)])
        if state == 'subscribed':
            # We must subscribe unsubscribed rules only
            unsubscribed_rules = active_rules.filtered(
                lambda r: r.state != 'subscribed')
            self._logger.warning('>>> unsubscribed_rules: {}'.format(unsubscribed_rules))
            unsubscribed_rules.subscribe()
        else:
            # We must unsubscribe subscribed rules only
            subscribed_rules = active_rules.filtered(
                lambda r: r.state != 'draft')
            self._logger.warning('>>> subscribed_rules: {}'.format(subscribed_rules))
            subscribed_rules.unsubscribe()
        return {
            'name': _('Rules'),
            'views': [(False, 'tree'), (False, 'form'),],
            'res_model': 'auditlog.rule',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'flags': {'tree': {'action_buttons': True},
                      'form': {'action_buttons': True},}
        }
