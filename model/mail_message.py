# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import base64
from openerp.osv.orm import Model, browse_record
from openerp.osv import fields

class MailMessage(Model):
    _inherit = 'mail.message'

    def fetchmail_inbox_attach_existing(self, cr, uid, ids, context=None):
        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'fetchmail.inbox.attach.existing.wizard',
                'context': {
                    'default_mail_id': ids and ids[0],
                    },
                }

    def fetchmail_inbox_create(self, cr, uid, ids, context=None):
        if context and context.get('default_res_model'):
            model_id = self.pool.get('ir.model').search(
                    cr, uid, [('model', '=', context['default_res_model'])],
                    context=None)
            model_id = model_id and model_id[0]
            wizard_model = self.pool.get('fetchmail.inbox.create.wizard')
            return wizard_model.button_create(
                    cr, uid,
                    [wizard_model.create(
                        cr, uid,
                        {
                            'model_id': model_id,
                            'mail_id': ids and ids[0],
                        },
                        context=context)],
                    context=context)

        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'fetchmail.inbox.create.wizard',
                'context': {
                    'default_mail_id': ids and ids[0],
                    },
                }

    def fetchmail_inbox_to_msg_dict(self, cr, uid, ids, context=None):
        '''
        return a dict to be consumed by mail_thread.message_{new,update}
        ideally, the original mail is attached, otherwise, try toyield a
        similar result to mail_thread.message_parse()
        '''
        result = {}

        for this in self.browse(cr, uid, ids, context=None):
            msg = {'attachments': []}
            for attachment in this.attachment_ids:
                name_data = (attachment.datas_fname,
                        base64.b64decode(attachment.datas))
                #reparse original message if available
                if name_data[0] == 'original_email.eml':
                    return self.pool.get('mail.thread').message_parse(
                            cr, uid, name_data[1],
                            save_original=False, context=context)
                msg['attachments'].append(name_data)
            for field in ['type', 'author_id', 'message_id', 'subject',
                    'email_from', 'date', 'parent_id', 'body']:
                if isinstance(this[field], browse_record):
                    msg[field] = this[field].id
                else:
                    msg[field] = this[field] or ''
            msg['from'] = this.author_id.email or ''
            msg['to'] = ','.join([p.email for p in this.partner_ids])
            msg['partner_ids'] = [(4, p.id) for p in this.partner_ids]
            result[this.id] = msg

        return result if len(ids) > 1 else result[ids[0]]

    def fetchmail_inbox_move_to_record(self, cr, uid, ids, res_model, res_id,
                                       context=None):
        '''move message to object given by res_model and res_id'''
        for this in self.browse(cr, uid, ids, context=context):
            inbox_model = self.pool.get(this.model)
            inbox_ids = inbox_model.search(
                    cr, uid, [('message_ids', 'in', ids)], context=context)
            this.write({
                'model': res_model,
                'res_id': res_id,
                })
            inbox_model.unlink(cr, uid, inbox_ids, context=context)

            for attachment in this.attachment_ids:
                if context.get('fetchmail_invoice_delete_original', True) and\
                        attachment.datas_fname == 'original_email.eml':
                    attachment.unlink()
                    continue
                if context.get('fetchmail_invoice_move_attachments', True):
                    attachment.write({
                        'res_model': res_model,
                        'res_id': res_id,
                        })

    def _needaction_count(self, cr, uid, dom, context=None):
        if dom == [('model', '=', 'fetchmail.inbox')]:
            return len(self.search(cr, uid, dom, context=context))
        return super(MailMessage, self)._needaction_count(
                cr, uid, dom, context=context)
