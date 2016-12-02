# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta
import random
import string
from openerp import api, fields, models
from openerp.exceptions import AccessDenied, ValidationError
from ..exceptions import MfaTokenInvalidError, MfaTokenExpiredError


class ResUsers(models.Model):
    _inherit = 'res.users'

    mfa_enabled = fields.Boolean(string='MFA Enabled?')
    authenticator_ids = fields.One2many(
        comodel_name='res.users.authenticator',
        inverse_name='user_id',
        string='Authentication Apps/Devices',
        help='To delete an authentication app, remove it from this list. To'
        ' add a new authentication app, please use the button to the right.',
    )
    mfa_login_token = fields.Char()
    mfa_login_token_exp = fields.Datetime()
    trusted_device_ids = fields.One2many(
        comodel_name='res.users.device',
        inverse_name='user_id',
    )

    @api.multi
    @api.constrains('mfa_enabled', 'authenticator_ids')
    def _check_enabled_with_authenticator(self):
        for record in self:
            if record.mfa_enabled and not record.authenticator_ids:
                raise ValidationError(
                    'You have MFA enabled but do not have any authentication'
                    ' apps/devices set up. To keep from being locked out,'
                    ' please add one before you activate this feature.'
                )

    @api.model
    def check_credentials(self, password):
        try:
            super(ResUsers, self).check_credentials(password)
        except AccessDenied:
            user = self.sudo().search([
                ('id', '=', self.env.uid),
                ('mfa_login_token', '=', password),
            ])
            user._user_from_mfa_login_token_validate()

    @api.multi
    def generate_mfa_login_token(self, lifetime_mins=15):
        char_set = string.ascii_letters + string.digits

        for record in self:
            record.mfa_login_token = ''.join(
                random.SystemRandom().choice(char_set) for __ in xrange(20)
            )

            expiration = datetime.now() + timedelta(minutes=lifetime_mins)
            record.mfa_login_token_exp = fields.Datetime.to_string(expiration)

    @api.model
    def user_from_mfa_login_token(self, token):
        if not token:
            raise MfaTokenInvalidError()

        user = self.search([('mfa_login_token', '=', token)])
        user._user_from_mfa_login_token_validate()

        return user

    @api.multi
    def _user_from_mfa_login_token_validate(self):
        if not len(self) == 1:
            raise MfaTokenInvalidError()
        if self.mfa_login_token_exp < fields.Datetime.now():
            raise MfaTokenExpiredError()

    @api.multi
    def validate_mfa_confirmation_code(self, confirmation_code):
        self.ensure_one()
        return self.authenticator_ids.validate_conf_code(confirmation_code)
