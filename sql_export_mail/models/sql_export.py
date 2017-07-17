# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Akretion (<http://www.akretion.com>).
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

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning as UserError
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID


class SqlExport(models.Model):
    _inherit = 'sql.export'

    mail_user_ids = fields.Many2many(
        'res.users',
        'mail_user_sqlquery_rel',
        'sql_id',
        'user_id',
        'User to notify',
        help='Add the users who want to receive the report by e-mail. You '
        'need to link the sql query with a cron to send mail automatically')
    cron_ids = fields.Many2many(
        'ir.cron',
        'cron_sqlquery_rel',
        'sql_id',
        'cron_id',
        'Crons')
    # We could implement other conditions, that is why it is a selection field
    mail_condition = fields.Selection(
        [('not_empty', 'File Not Empty')], default='not_empty')

    @api.multi
    def create_cron(self):
        self.ensure_one()
        nextcall = datetime.now() + timedelta(hours=2)
        nextcall_fmt = datetime.strftime(nextcall,
                                         DEFAULT_SERVER_DATETIME_FORMAT)
        cron_vals = {
            'active': True,
            'model': 'sql.export',
            'function': '_run_all_sql_export_for_cron',
            'name': 'SQL Export : %s' % self.name,
            'nextcall': nextcall_fmt,
            'doall': False,
            'numbercall': -1,
            'user_id': SUPERUSER_ID,
        }
        cron = self.env['ir.cron'].create(cron_vals)
        write_vals = {'args': '[[%s]]' % cron.id}
        cron.write(write_vals)

        self.write({'cron_ids': [(4, cron.id)]})

    @api.one
    def send_mail(self, params=None):
        mail_template = self.env.ref('sql_export_mail.sql_export_mailer')
        now_time = datetime.strftime(datetime.now(),
                                     DEFAULT_SERVER_DATETIME_FORMAT)
        attach_obj = self.env['ir.attachment']
        if self.mail_condition == 'not_empty':
            res = self._execute_sql_request(
                params=params, mode='fetchone')
            if not res:
                return

        binary = self._execute_sql_request(
            params=params, mode='stdout', copy_options=self.copy_options)
        attach_vals = {
            'name': now_time + ' - ' + self.name,
            'datas_fname': now_time + ' - ' + self.name + '.csv',
            'datas': binary,
        }
        attachment = attach_obj.create(attach_vals)
        msg_id = mail_template.send_mail(self.id, force_send=False)
        mail = self.env['mail.mail'].browse(msg_id)
        mail.write({'attachment_ids': [(4, attachment.id)]})

    @api.model
    def _run_all_sql_export_for_cron(self, cron_ids):
        exports = self.search([('cron_ids', 'in', cron_ids)])
        for export in exports:
            if "%(company_id)s" in export.query and \
                    "%(user_id)s" not in export.query:
                variable_dict = {}
                companies = self.env['res.company'].search([])
                for company in companies:
                    users = export.mail_user_ids.filtered(
                        lambda u: u.company_id == company)
                    if users:
                        variable_dict['company_id'] = users[0].company_id.id
                        export.with_context(mail_to=users.ids).send_mail(
                            params=variable_dict)
            elif "%(user_id)s" in export.query:
                variable_dict = {}
                for user in export.mail_user_ids:
                    variable_dict['user_id'] = user.id
                    if "%(company_id)s" in export.query:
                        variable_dict['company_id'] = user.company_id.id
                    export.with_context(mail_to=[user.id]).send_mail(
                        params=variable_dict)
            else:
                export.send_mail()

    @api.one
    @api.constrains('field_ids', 'mail_user_ids')
    def check_no_parameter_if_sent_by_mail(self):
        if self.field_ids and self.mail_user_ids:
            raise UserError(_(
                "It is not possible to execute and send a query automatically"
                " by e-mail if there are parameters to fill"))

    @api.one
    @api.constrains('mail_user_ids')
    def check_mail_user(self):
        for user in self.mail_user_ids:
            if not user.email:
                raise UserError(_(
                    "The user does not have any e-mail address."))

    @api.multi
    def get_email_address_for_template(self):
        """
            Called from mail template
        """
        self.ensure_one()
        if self.env.context.get('mail_to'):
            mail_users = self.env['res.users'].browse(
                self.env.context.get('mail_to'))
        else:
            mail_users = self.mail_user_ids
        emails = ''
        for user in mail_users:
            if emails and user.email:
                emails += ',' + user.email
            elif user.email:
                emails += user.email
        return emails
