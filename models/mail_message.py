# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
from odoo import api, models


class MailMessage(models.Model):
    _inherit = 'mail.message'

    @api.multi
    def fetchmail_inbox_attach_existing(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'fetchmail.inbox.attach.existing.wizard',
            'context': {
                'default_mail_id': self.ids and self.ids[0],
            },
        }

    @api.multi
    def fetchmail_inbox_create(self):
        if self.env.context.get('set_default_res_model'):
            model_id = self.env['ir.model'].search([
                ('model', '=', self.env.context['set_default_res_model']),
            ], limit=1)[:1].id
            wizard_model = self.env['fetchmail.inbox.create.wizard']
            return wizard_model.create({
                'model_id': model_id,
                'mail_id': self.ids and self.ids[0],
            }).button_create()

        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'fetchmail.inbox.create.wizard',
            'context': {
                'default_mail_id': self.ids and self.ids[0],
            },
        }

    @api.multi
    def fetchmail_inbox_to_msg_dict(self):
        '''
        return a dict to be consumed by mail_thread.message_{new,update}
        ideally, the original mail is attached, otherwise, try to yield a
        similar result to mail_thread.message_parse()
        '''
        result = {}

        for this in self:
            msg = {'attachments': []}
            for attachment in this.attachment_ids:
                name_data = (
                    attachment.datas_fname,
                    base64.b64decode(attachment.datas),
                )
                # reparse original message if available
                if name_data[0] == 'original_email.eml':
                    return self.env['mail.thread'].message_parse(
                        name_data[1], save_original=False)
                msg['attachments'].append(name_data)
            for field in ['author_id', 'message_id', 'subject',
                          'email_from', 'date', 'parent_id', 'body']:
                if isinstance(this[field], models.BaseModel):
                    msg[field] = this[field].id
                else:
                    msg[field] = this[field] or ''
            msg['from'] = this.author_id.email or this['email_from'] or ''
            msg['to'] = ','.join([p.email for p in this.partner_ids])
            msg['partner_ids'] = [(4, p.id) for p in this.partner_ids]
            result[this.id] = msg

        return result if len(self.ids) > 1 else result[self.ids[0]]

    @api.multi
    def fetchmail_inbox_move_to_record(self, res_model, res_id):
        '''move message to object given by res_model and res_id'''
        for this in self:
            inbox_model = self.env[this.model]
            inbox = inbox_model.search([('message_ids', 'in', this.ids)])
            this.write({
                'model': res_model,
                'res_id': res_id,
            })
            for attachment in this.attachment_ids:
                if attachment.datas_fname == 'original_email.eml' and\
                        self.env.context.get('fetchmail_inbox_delete_original',
                                             True):
                    attachment.unlink()
                    break
            if self.env.context.get('fetchmail_inbox_move_attachments', True):
                this.attachment_ids.write({
                    'res_model': res_model,
                    'res_id': res_id,
                })
            inbox.unlink()

    @api.model
    def _needaction_count(self, dom):
        """ Needaction is true for every message on this record, regardless
        of read status """
        if dom == [('model', '=', 'fetchmail.inbox')]:
            return self.search(dom, count=True)
        return super(MailMessage, self)._needaction_count(dom)
