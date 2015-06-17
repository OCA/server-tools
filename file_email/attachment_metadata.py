# -*- coding: utf-8 -*-
###############################################################################
#
#   file_email for OpenERP
#   Copyright (C) 2012-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api
import base64


class IrAttachmentMetadata(models.Model):
    _inherit = "ir.attachment.metadata"

    fetchmail_server_id = fields.Many2one('fetchmail.server',
                                          string='Email Server')

    def message_process(self, cr, uid, model, message, custom_values=None,
                        save_original=False, strip_attachments=False,
                        thread_id=None, context=None):
        if context is None:
            context = {}
        context['no_post'] = True
        return True

    def message_post(self, cr, uid, thread_id, body='', subject=None,
                     type='notification', subtype=None, parent_id=False,
                     attachments=None, content_subtype='html', context=None,
                     **kwargs):
        if context.get('no_post'):
            return None
        return True

    @api.model
    def _get_attachment_metadata_data(self, condition, msg, att):
        values = {
            'file_type': condition.server_id.file_type,
            'name': msg['subject'],
            'direction': 'input',
            'date': msg['date'],
            'ext_id': msg['message_id'],
            'datas_fname': att[0],
            'datas': base64.b64encode(att[1]),
            'state': 'pending'
        }
        return values

    @api.model
    def prepare_data_from_basic_condition(self, condition, msg):
        vals = {}
        if (condition.from_email in msg['from']
                and condition.mail_subject in msg['subject']):
            for att in msg['attachments']:
                if condition.file_extension in att[0]:
                    vals = self._get_attachment_metadata_data(condition,
                                                              msg, att)
                    break
        return vals

    @api.model
    def _prepare_data_for_attachment_metadata(self, msg):
        """Method to prepare the data for creating a attachment metadata.
        :param msg: a dictionnary with the email data
        :type: dict

        :return: a list of dictionnary that containt
            the attachment metadata data
        :rtype: list
        """
        res = []
        server_id = self._context.get('fetchmail_server_id', False)
        file_condition_obj = self.env['ir.attachment.metadata.condition']
        cond_ids = file_condition_obj.search([('server_id', '=', server_id)])
        if cond_ids:
            for cond in cond_ids:
                if cond.type == 'normal':
                    vals = self.prepare_data_from_basic_condition(cond, msg)
                else:
                    vals = getattr(self, cond.type)(cond, msg)
                if vals:
                    res.append(vals)
        return res

    @api.model
    def message_new(self, msg, custom_values):
        created_ids = []
        res = self._prepare_data_for_attachment_metadata(msg)
        if res:
            for vals in res:
                default = self._context.get('default_attachment_metadata_vals')
                if default:
                    for key in default:
                        if key not in vals:
                            vals[key] = default[key]
                created_ids.append(self.create(vals))
                self._cr.commit()
            return created_ids[0].id
        return None


class IrAttachmentMetadataCondition(models.Model):
    _name = "ir.attachment.metadata.condition"
    _description = "Attachment Metadata Conditions"

    @api.model
    def _get_attachment_metadata_condition_type(self):
        return self.get_attachment_metadata_condition_type()

    def get_attachment_metadata_condition_type(self):
        return [('normal', 'Normal')]

    from_email = fields.Char(string='Email', size=64)
    mail_subject = fields.Char(size=64)
    type = fields.Selection(
        selection='_get_attachment_metadata_condition_type',
        help="Create your own type if the normal type \
                    do not correspond to your need",
        required=True,
        default='normal'
        )
    file_extension = fields.Char(size=64,
                                 help="File extension or file name",
                                 required=True)
    server_id = fields.Many2one('fetchmail.server', string='Server Mail')
