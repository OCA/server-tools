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
        'Latest password update', readonly=True
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
        message = [
            'Password must be %d characters or more.' %
            company_id.password_length
        ]
        message.append('Must contain the following:')
        if company_id.password_lower:
            message.append('* Lowercase letter')
        if company_id.password_upper:
            message.append('* Uppercase letter')
        if company_id.password_numeric:
            message.append('* Numeric digit')
        if company_id.password_special:
            message.append('* Special character')
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
