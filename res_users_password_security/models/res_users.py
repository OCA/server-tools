# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta
import re

from openerp import api, fields, models, _
from openerp.addons.res_users_password_security.exceptions import PassError


def delta_now(**kwargs):
    dt = datetime.now() + timedelta(**kwargs)
    return fields.Datetime.to_string(dt)


class ResUsers(models.Model):
    _inherit = 'res.users'

    password_write_date = fields.Datetime(
        'Last password update',
        readonly=True,
    )
    password_history_ids = fields.One2many(
        string='Password History',
        comodel_name='res.users.pass.history',
        inverse_name='user_id',
        readonly=True,
    )

    @api.multi
    @api.constrain('password_crypt')
    def _check_password_crypt(self):
        for rec_id in self:
            recent_passes = rec_id.password.history_ids.limit(
                rec_id.company_id.password_history
            )
            if len(recent_passes.filtered(
                lambda r: r.password_crypt == rec_id.password_crypt
            )):
                raise PassError(
                    _('Cannot use the most recent %d passwords') %
                    rec_id.company_id.password_history
                )

    @api.model
    def create(self, vals):
        vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('password'):
            self.check_password(vals['password'])
            vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).write(vals)

    @api.multi
    def password_match_message(self):
        company_id = self.company_id
        message = []
        if company_id.password_lower:
            message.append('* ' + _('Lowercase letter'))
        if company_id.password_upper:
            message.append('* ' + _('Uppercase letter'))
        if company_id.password_numeric:
            message.append('* ' + _('Numeric digit'))
        if company_id.password_special:
            message.append('* ' + _('Special character'))
        if len(message):
            message = [_('Must contain the following:')]
        if company_id.password_length:
            message = [
                _('Password must be %d characters or more.') %
                company_id.password_length
            ] + message
        return '\r'.join(message)

    @api.multi
    def check_password(self, password):
        if not password:
            return True
        company_id = self.company_id
        password_regex = ['^']
        if company_id.password_lower:
            password_regex.append('(?=.*?[a-z])')
        if company_id.password_upper:
            password_regex.append('(?=.*?[A-Z])')
        if company_id.password_numeric:
            password_regex.append(r'(?=.*?\d)')
        if company_id.password_special:
            password_regex.append(r'(?=.*?\W)')
        password_regex.append('.{%d,}$' % company_id.password_length)
        if not re.search(''.join(password_regex), password):
            raise PassError(_(self.password_match_message()))
        return True

    @api.multi
    def _password_has_expired(self):
        if not self.password_write_date:
            return True
        write_date = fields.Datetime.from_string(self.password_write_date)
        today = fields.Datetime.from_string(fields.Datetime.now())
        days = (today - write_date).days
        return (days > self.company_id.password_expiration)

    @api.multi
    def action_expire_password(self):
        expiration = delta_now(days=+1)
        for rec_id in self:
            rec_id.mapped('partner_id').signup_prepare(
                signup_type="reset", expiration=expiration
            )

    @api.multi
    @api.depends('password_crypt')
    def _save_password_crypt(self):
        """ It saves password crypt history for history rules """
        for rec_id in self:
            self.env['res.users.pass.history'].create({
                'user_id': rec_id,
                'password_crypt': rec_id.password_crypt,
            })
