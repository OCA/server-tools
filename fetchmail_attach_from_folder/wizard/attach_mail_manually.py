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

from openerp.osv import fields
from openerp.osv.orm import TransientModel
import logging
logger = logging.getLogger(__name__)


class attach_mail_manually(TransientModel):
    _name = 'fetchmail.attach.mail.manually'

    _columns = {
        'folder_id': fields.many2one('fetchmail.server.folder', 'Folder',
                                     readonly=True),
        'mail_ids': fields.one2many(
            'fetchmail.attach.mail.manually.mail', 'wizard_id', 'Emails'),
    }

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
                logger.error('Could not search mailbox %s on %s' % (
                    folder.path, folder.server_id.name))
                continue
            attach_mail_manually_mail._columns['object_id'].selection = [
                (folder.model_id.model, folder.model_id.name)]
            for msgid in msgids[0].split():
                result, msgdata = connection.fetch(msgid, '(RFC822)')
                if result != 'OK':
                    logger.error('Could not fetch %s in %s on %s' % (
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
                    'object_id': folder.model_id.model + ',False'
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
                    logger.error('Could not fetch %s in %s on %s' % (
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


class attach_mail_manually_mail(TransientModel):
    _name = 'fetchmail.attach.mail.manually.mail'

    _columns = {
        'wizard_id': fields.many2one('fetchmail.attach.mail.manually',
                                     readonly=True),
        'msgid': fields.char('Message id', size=16, readonly=True),
        'subject': fields.char('Subject', size=128, readonly=True),
        'date': fields.datetime('Date', readonly=True),
        'object_id': fields.reference(
            'Object',
            selection=lambda self, cr, uid, context: [
                (m.model, m.name)
                for m in self.pool.get('ir.model').browse(
                    cr, uid,
                    self.pool.get('ir.model').search(cr, uid, []),
                    context
                )
            ],
            size=128,
        ),
    }
