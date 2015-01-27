# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#    All Rights Reserved
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
from openerp import fields, models
import logging


class attach_mail_manually(models.TransientModel):
    _name = 'fetchmail.attach.mail.manually'

    folder_id = fields.Many2one(
        'fetchmail.server.folder', 'Folder', readonly=True)
    mail_ids = fields.One2many(
        'fetchmail.attach.mail.manually.mail', 'wizard_id', 'Emails')

    def default_get(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}

        defaults = super(attach_mail_manually, self).default_get(
            cr, uid, fields_list, context
        )

        for folder in self.pool.get('fetchmail.server.folder').browse(
                cr, uid,
                [context.get('default_folder_id')], context):
            defaults['mail_ids'] = []
            connection = folder.server_id.connect()
            connection.select(folder.path)
            result, msgids = connection.search(
                None,
                'FLAGGED' if folder.flag_nonmatching else 'UNDELETED')
            if result != 'OK':
                logging.error('Could not search mailbox %s on %s' % (
                    folder.path, folder.server_id.name))
                continue
            for msgid in msgids[0].split():
                result, msgdata = connection.fetch(msgid, '(RFC822)')
                if result != 'OK':
                    logging.error('Could not fetch %s in %s on %s' % (
                        msgid, folder.path, folder.server_id.name))
                    continue
                mail_message = self.pool.get('mail.thread').message_parse(
                    cr, uid, msgdata[0][1],
                    save_original=folder.server_id.original,
                    context=context
                )
                defaults['mail_ids'].append((0, 0, {
                    'msgid': msgid,
                    'subject': mail_message.get('subject', ''),
                    'date': mail_message.get('date', ''),
                    'object_id': '%s,-1' % folder.model_id.model,
                }))
            connection.close()

        return defaults

    def attach_mails(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids, context):
            for mail in this.mail_ids:
                connection = this.folder_id.server_id.connect()
                connection.select(this.folder_id.path)
                result, msgdata = connection.fetch(mail.msgid, '(RFC822)')
                if result != 'OK':
                    logging.error('Could not fetch %s in %s on %s' % (
                        mail.msgid, this.folder_id.path, this.server))
                    continue

                mail_message = self.pool.get('mail.thread').message_parse(
                    cr, uid, msgdata[0][1],
                    save_original=this.folder_id.server_id.original,
                    context=context)

                this.folder_id.server_id.attach_mail(
                    connection,
                    mail.object_id.id, this.folder_id, mail_message,
                    mail.msgid
                )
                connection.close()
        return {'type': 'ir.actions.act_window_close'}

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        result = super(attach_mail_manually, self).fields_view_get(
            cr, user, view_id, view_type, context, toolbar, submenu)

        tree = result['fields']['mail_ids']['views']['tree']
        for folder in self.pool['fetchmail.server.folder'].browse(
                cr, user, [context.get('default_folder_id')], context):
            tree['fields']['object_id']['selection'] = [
                (folder.model_id.model, folder.model_id.name)
            ]

        return result


class attach_mail_manually_mail(models.TransientModel):
    _name = 'fetchmail.attach.mail.manually.mail'

    wizard_id = fields.Many2one(
        'fetchmail.attach.mail.manually', readonly=True)
    msgid = fields.Char('Message id', readonly=True)
    subject = fields.Char('Subject', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    object_id = fields.Reference(
        lambda self: [
            (m.model, m.name)
            for m in self.env['ir.model'].search([])
        ],
        string='Object')
