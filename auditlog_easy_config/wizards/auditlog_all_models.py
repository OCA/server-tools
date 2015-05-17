from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
# import logging
# _logger = logging.getLogger(__name__)


class auditlog_all_models_wizard(models.TransientModel):
    _name = 'auditlog.all.models.wizard'
    
    FORBIDDEN_MODELS = ['auditlog.log', 'auditlog.log.line', 'auditlog.rule',
                        'audittail.rules.users', 'auditlog.all.models.wizard']

    log_create = fields.Boolean(string='Log creates', default=True,
                                help='Select this if you want to keep track '
                                     'of creation on all records of every '
                                     'existing model.')
    log_write = fields.Boolean(string='Log writes', default=True,
                               help='Select this if you want to keep track '
                                    'of modifications on all records of every '
                                    'existing model.')
    log_unlink = fields.Boolean(string='Log deletes', default=True,
                                help='Select this if you want to keep track '
                                     'of deletion on all records of every '
                                     'existing model.')
    overwrite_rules = fields.Boolean(string='Overwrite all existing rules',
                                     default=False,
                                     help='Select this if you want to '
                                          'overwrite the current existing '
                                          'rules in the database.')

    @api.multi
    def edit_selected(self):
        """Set selected rules options for auditing changes on
        corresponding models."""
        selected_rules_ids = self.env.context.get('active_ids')
        selected_rules = self.env['auditlog.rule'].browse(selected_rules_ids)
        selected_rules.write({
            'log_write': self.log_write,
            'log_unlink': self.log_unlink,
            'log_create': self.log_create,
        })
        return {'type': 'ir.actions.act_window_close'}
        # return {
        #     'name': _('Rules'),
        #     'views': [(False, 'tree'), (False, 'form'),],
        #     'res_model': 'auditlog.rule',
        #     'type': 'ir.actions.act_window',
        #     'target': 'current',
        #     'flags': {'tree': {'action_buttons': True},
        #               'form': {'action_buttons': True},}
        # }

    @api.multi
    def create_all(self, models):
        """Create rule for auditing changes on
        every model existing in the database."""
        new_records_ids = []
        rule_obj = self.env['auditlog.rule']
        for model in models:
            vals = {
                'name': model.name,
                'model_id': model.id,
                'log_read': False,
                'log_write': self.log_write,
                'log_unlink': self.log_unlink,
                'log_create': self.log_create,
            }
            new_record = rule_obj.create(vals)
            new_records_ids.append(new_record.id)
        return rule_obj.search([('id', 'in', new_records_ids)])

    @api.multi
    def subscribe_all(self):
        """Create -if necessary- and subscribe rule for auditing changes on
        every model existing in the database."""
        existing_rules = self.env['auditlog.rule'].search([])
        existing_rules_models_ids = existing_rules.mapped('model_id.id')
        if self.overwrite_rules:
            existing_rules.write({
                'log_write': self.log_write,
                'log_unlink': self.log_unlink,
                'log_create': self.log_create,
            })
            unsubscribed_rules = existing_rules.filtered(
                lambda r: r.state != 'subscribed')
            unsubscribed_rules.subscribe()
        models = self.env['ir.model'].search(
            [('model', 'not in', self.FORBIDDEN_MODELS),
             ('id', 'not in', existing_rules_models_ids)]
        )
        rules = self.create_all(models)
        rules.subscribe()
        return {
            'name': _('Rules'),
            'views': [(False, 'tree'), (False, 'form'),],
            'res_model': 'auditlog.rule',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'flags': {'tree': {'action_buttons': True},
                      'form': {'action_buttons': True},}
        }
