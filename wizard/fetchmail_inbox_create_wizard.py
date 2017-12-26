# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class FetchmailInboxCreateWizard(models.TransientModel):
    _name = 'fetchmail.inbox.create.wizard'
    _description = 'Create object from mail'

    model_id = fields.Many2one('ir.model', 'Model', required=True)
    mail_id = fields.Many2one('mail.message', 'Email', required=True)

    @api.multi
    def button_create(self):
        for this in self:
            model = self.env[this.model_id.model]

            if hasattr(model, 'message_new'):
                object_id = model.with_context(from_fetchmail_inbox=True)\
                    .message_new(this.mail_id.fetchmail_inbox_to_msg_dict())
            else:
                object_id = model.create({}).id

            this.mail_id.fetchmail_inbox_move_to_record(
                    this.model_id.model, object_id)

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': this.model_id.model,
            'res_id': object_id,
        }
