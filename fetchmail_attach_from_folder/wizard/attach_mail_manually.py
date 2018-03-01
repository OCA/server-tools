# -*- coding: utf-8 -*-
# Copyright - 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from odoo import api, fields, models


_logger = logging.getLogger(__name__)


class AttachMailManually(models.TransientModel):
    _name = 'fetchmail.attach.mail.manually'

    folder_id = fields.Many2one(
        'fetchmail.server.folder', 'Folder', readonly=True)
    mail_ids = fields.One2many(
        'fetchmail.attach.mail.manually.mail', 'wizard_id', 'Emails')

    @api.model
    def default_get(self, fields_list):
        folder_model = self.env['fetchmail.server.folder']
        thread_model = self.env['mail.thread']
        defaults = super(AttachMailManually, self).default_get(fields_list)
        default_folder_id = self.env.context.get('default_folder_id')
        for folder in folder_model.browse([default_folder_id]):
            defaults['mail_ids'] = []
            connection = folder.server_id.connect()
            connection.select(folder.path)
            result, msgids = connection.search(
                None,
                'FLAGGED' if folder.flag_nonmatching else 'UNDELETED')
            if result != 'OK':
                _logger.error(
                    'Could not search mailbox %s on %s',
                    folder.path, folder.server_id.name)
                continue
            for msgid in msgids[0].split():
                result, msgdata = connection.fetch(msgid, '(RFC822)')
                if result != 'OK':
                    _logger.error(
                        'Could not fetch %s in %s on %s',
                        msgid, folder.path, folder.server_id.name)
                    continue
                mail_message = thread_model.message_parse(
                    msgdata[0][1],
                    save_original=folder.server_id.original)
                defaults['mail_ids'].append((0, 0, {
                    'msgid': msgid,
                    'subject': mail_message.get('subject', ''),
                    'date': mail_message.get('date', ''),
                    'object_id': '%s,-1' % folder.model_id.model}))
            connection.close()
        return defaults

    @api.multi
    def attach_mails(self):
        thread_model = self.env['mail.thread']
        for this in self:
            folder = this.folder_id
            server = folder.server_id
            connection = server.connect()
            connection.select(folder.path)
            for mail in this.mail_ids:
                if not mail.object_id:
                    continue
                result, msgdata = connection.fetch(mail.msgid, '(RFC822)')
                if result != 'OK':
                    _logger.error(
                        'Could not fetch %s in %s on %s',
                        mail.msgid, folder.path, server)
                    continue
                mail_message = thread_model.message_parse(
                    msgdata[0][1], save_original=server.original)
                folder.attach_mail(mail.object_id, mail_message)
                if folder.delete_matching:
                    connection.store(mail.msgid, '+FLAGS', '\\DELETED')
                elif folder.flag_nonmatching:
                    connection.store(mail.msgid, '-FLAGS', '\\FLAGGED')
            connection.close()
        return {'type': 'ir.actions.act_window_close'}

    @api.model
    def fields_view_get(
            self, view_id=None, view_type='form',
            toolbar=False, submenu=False):
        result = super(AttachMailManually, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        tree = result['fields']['mail_ids']['views']['tree']
        folder_model = self.env['fetchmail.server.folder']
        default_folder_id = self.env.context.get('default_folder_id')
        for folder in folder_model.browse([default_folder_id]):
            tree['fields']['object_id']['selection'] = [
                (folder.model_id.model, folder.model_id.name)]
        return result


class AttachMailManuallyMail(models.TransientModel):
    _name = 'fetchmail.attach.mail.manually.mail'

    wizard_id = fields.Many2one(
        'fetchmail.attach.mail.manually', readonly=True)
    msgid = fields.Char('Message id', readonly=True)
    subject = fields.Char('Subject', readonly=True)
    date = fields.Datetime('Date', readonly=True)
    object_id = fields.Reference(
        lambda self: [
            (m.model, m.name)
            for m in self.env['ir.model'].search([])],
        string='Object')
