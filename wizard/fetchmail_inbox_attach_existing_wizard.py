# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, fields, models
from openerp.exceptions import Warning as UserError


class FetchmailInboxAttachExistingWizard(models.TransientModel):
    _name = 'fetchmail.inbox.attach.existing.wizard'
    _description = 'Attach mail to existing object'

    res_model = fields.Char('Model')
    res_id = fields.Integer('Object', required=True)
    res_reference = fields.Reference(
        lambda self: [
            (m.model, m.name) for m in self.env['ir.model'].search([])
        ], 'Reference')
    mail_id = fields.Many2one('mail.message', 'Email', required=True)

    @api.model
    def default_get(self, fields_list):
        if self.env.context.get('set_default_res_model'):
            self = self.with_context(
                default_res_model=self.env.context['set_default_res_model'])
        return super(FetchmailInboxAttachExistingWizard, self).default_get(
            fields_list)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        result = super(FetchmailInboxAttachExistingWizard, self)\
            .fields_view_get(
                view_id=view_id, view_type=view_type, toolbar=toolbar,
                submenu=submenu)
        # Can't use the standard 'default_' key because it is purged
        # in between actions to prevent erratic defaults for other models
        if self.env.context.get('set_default_res_model'):
            result['fields']['res_id']['type'] = 'many2one'
            result['fields']['res_id']['relation'] = \
                self.env.context['set_default_res_model']
            result['fields']['res_id']['context'] = {}
        return result

    @api.multi
    def button_attach(self):
        self.ensure_one()
        for this in self:
            if this.res_model and this.res_id:
                res_model = this.res_model
                res_id = this.res_id
            elif this.res_reference:
                res_model = this.res_reference._model._name
                res_id = this.res_reference.id
            else:
                raise UserError(_('You have to select an object!'))

            model = self.env[res_model]
            if hasattr(model, 'message_update'):
                model.browse([res_id]).with_context(from_fetchmail_inbox=True)\
                    .message_update(this.mail_id.fetchmail_inbox_to_msg_dict())

            this.mail_id.fetchmail_inbox_move_to_record(res_model, res_id)
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': this.res_model or this.res_reference._model._name,
            'res_id': this.res_id or this.res_reference.id,
        }
