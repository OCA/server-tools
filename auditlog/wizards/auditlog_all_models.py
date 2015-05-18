# -*- coding: utf-8 -*-
# License, author and contributors information in:
# __openerp__.py file at the root folder of this module.

from openerp import models, fields, api, _


class AuditlogAllModelsWizard(models.TransientModel):
    _name = 'auditlog.all.models.wizard'

    FORBIDDEN_MODELS = ['auditlog.log', 'auditlog.log.line', 'auditlog.rule',
                        'audittail.rules.users', 'auditlog.all.models.wizard']
    log_create = fields.Boolean(
        string=u'Log Creates',
        default=True,
        help=(u'Select this if you want to keep track of creation on any '
              u'record of existing models.'))
    log_read = fields.Boolean(
        string=u'Log Reads',
        help=(u'Select this if you want to keep track of read/open on any '
              u'record of existing models.'))
    log_write = fields.Boolean(
        string=u'Log Writes',
        default=True,
        help=(u'Select this if you want to keep track of modifications on any '
              u'record of existing models.'))
    log_unlink = fields.Boolean(
        string='Log Deletes',
        default=True,
        help=(u'Select this if you want to keep track of deletion on any '
              u'record of existing models.'))
    overwrite_rules = fields.Boolean(
        string='Overwrite all existing rules',
        default=False,
        help=(u'Select this if you want to overwrite the current existing '
              u'rules in the database.'))

    @api.multi
    def set_tracked_actions_selected(self):
        """Set selected rules tracked actions for auditing changes on
        corresponding models."""
        selected_rules_ids = self.env.context.get('active_ids')
        selected_rules = self.env['auditlog.rule'].browse(selected_rules_ids)
        selected_rules.write({
            'log_write': self.log_write,
            'log_unlink': self.log_unlink,
            'log_create': self.log_create,
        })
        return {'type': 'ir.actions.act_window_close'}

    @api.multi
    def create_all(self, models):
        """Create rules for auditing changes on
        every model existing in the database."""
        rule_obj = self.env['auditlog.rule']
        new_records = rule_obj
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
            new_records += new_record
        return new_records

    @api.multi
    def subscribe_all(self):
        """Create -if necessary- and subscribe rules for auditing changes on
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
        new_rules = self.create_all(models)
        new_rules.subscribe()
        return {
            'name': _('Rules'),
            'views': [(False, 'tree'), (False, 'form'),],
            'res_model': 'auditlog.rule',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'flags': {'tree': {'action_buttons': True},
                      'form': {'action_buttons': True},}
        }
