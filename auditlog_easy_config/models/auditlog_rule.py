from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class auditlog_rule(models.Model):
    _inherit = 'auditlog.rule'

    @api.model
    def check_selected_rules_to_modify(self, mode='unsubscription'):
        if mode == 'subscription':
            state = 'subscribed'
            error_msg = _('There are selected rules which are already '
                          'subscribed. Please, uncheck them first.')
        else:
            state = 'draft'
            error_msg = _('There are selected rules which are already '
                          'unsubscribed. Please, uncheck them first.')
        active_ids = self.env.context.get('active_ids')
        active_rules = self.search([('id', 'in', active_ids)]) 
        if any(rule.state == state for rule in active_rules):
            raise ValidationError(error_msg)
        else:
            if mode == 'subscription':
                active_rules.subscribe()
            else:
                active_rules.unsubscribe()
        return {
            'name': _('Rules'),
            'views': [(False, 'tree'), (False, 'form'),],
            'res_model': 'auditlog.rule',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'flags': {'tree': {'action_buttons': True},
                      'form': {'action_buttons': True},}
        }