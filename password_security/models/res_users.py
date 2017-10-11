# -*- coding: utf-8 -*-
# Copyright 2017 Kaushal Prajapati <kbprajapati@live.com>.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import re

from datetime import datetime, timedelta

from odoo import api, fields, models, _

from ..exceptions import PassError


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

    @api.model
    def create(self, vals):
        vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('password'):
            self._check_password(vals['password'])
            vals['password_write_date'] = fields.Datetime.now()
        return super(ResUsers, self).write(vals)

    @api.multi
    def _check_password(self, password):
        self._check_password_rules(password)
        self._check_password_history(password)
        return True

    @api.multi
    def _check_password_rules(self, password):
        self.ensure_one()
        if not password:
            return True
        company_id = self.company_id
        message = []
        if company_id.password_lower and sum(map(str.islower, password)) < \
                company_id.password_lower:
            message.append('\n ' + _('Lowercase letter (At least ' +
                                     str(company_id.password_lower) +
                                     ' character)')
                           )
        if company_id.password_upper and sum(map(str.isupper, password)) < \
                company_id.password_upper:
            message.append('\n ' + _('Uppercase letter (At least ' +
                                     str(company_id.password_upper) +
                                     ' character)')
                           )
        if company_id.password_numeric and sum(map(str.isdigit, password)) < \
                company_id.password_numeric:
            message.append('\n ' + _('Numeric digit (At least ' +
                                     str(company_id.password_numeric) +
                                     ' numeric)')
                           )
        if company_id.password_special and len(set('[~!@#$%^&*()_+{}":;\']+$'
                                               ).intersection(
                password)) < company_id.password_numeric:
            message.append('\n ' + _('Special character (At least ' +
                                     str(company_id.password_special) +
                                     ' character of [ ~ ! @ # $ % ^ & * ( )_+ {'
                                     ' } " : ; \' ])')
                           )
        if company_id.password_length and len(password) < \
                company_id.password_length:
            message = [_('Password must be %d characters or more.') %
                       company_id.password_length] + message
        if len(message) > 0:
            raise PassError('\r'.join(message))
        else:
            return True

    @api.multi
    def _password_has_expired(self):
        self.ensure_one()
        if not self.password_write_date:
            return True
        write_date = fields.Datetime.from_string(self.password_write_date)
        today = fields.Datetime.from_string(fields.Datetime.now())
        days = (today - write_date).days
        return days > self.company_id.password_expiration

    @api.multi
    def action_expire_password(self):
        expiration = delta_now(days=+1)
        for rec_id in self:
            rec_id.mapped('partner_id').signup_prepare(
                signup_type="reset", expiration=expiration
            )

    @api.multi
    def _validate_pass_reset(self):
        """ It provides validations before initiating a pass reset email
        :raises: PassError on invalidated pass reset attempt
        :return: True on allowed reset
        """
        for rec_id in self:
            pass_min = rec_id.company_id.password_minimum
            if pass_min <= 0:
                pass
            write_date = fields.Datetime.from_string(
                rec_id.password_write_date
            )
            delta = timedelta(hours=pass_min)
            if write_date + delta > datetime.now():
                raise PassError(
                    _('Passwords can only be reset every %d hour(s). '
                      'Please contact an administrator for assistance.') %
                    pass_min,
                )
        return True

    @api.multi
    def _check_password_history(self, password):
        """ It validates proposed password against existing history
        :raises: PassError on reused password
        """
        crypt = self._crypt_context()
        for rec_id in self:
            recent_passes = rec_id.company_id.password_history
            if recent_passes < 0:
                recent_passes = rec_id.password_history_ids
            else:
                recent_passes = rec_id.password_history_ids[
                    0:recent_passes-1
                ]
            if recent_passes.filtered(
                    lambda r: crypt.verify(password, r.password_crypt)):
                raise PassError(
                    _('Cannot use the most recent %d passwords') %
                    rec_id.company_id.password_history
                )

    @api.multi
    def _set_encrypted_password(self, encrypted):
        """ It saves password crypt history for history rules """
        super(ResUsers, self)._set_encrypted_password(encrypted)
        self.write({
            'password_history_ids': [(0, 0, {
                'password_crypt': encrypted,
            })],
        })
