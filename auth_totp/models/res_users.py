# -*- coding: utf-8 -*-
# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from datetime import datetime, timedelta
import random
import string
from openerp import _, api, fields, models
from openerp.exceptions import AccessDenied, ValidationError
from ..exceptions import MfaTokenInvalidError, MfaTokenExpiredError


class ResUsers(models.Model):
    _inherit = 'res.users'

    @classmethod
    def _build_model(cls, pool, cr):
        model = super(ResUsers, cls)._build_model(pool, cr)
        ModelCls = type(model)
        ModelCls.SELF_WRITEABLE_FIELDS += ['mfa_enabled', 'authenticator_ids']
        return model

    mfa_enabled = fields.Boolean(string='MFA Enabled?')
    authenticator_ids = fields.One2many(
        comodel_name='res.users.authenticator',
        inverse_name='user_id',
        string='Authentication Apps/Devices',
        help='To delete an authentication app, remove it from this list. To'
             ' add a new authentication app, please use the button to the'
             ' right.',
    )
    mfa_login_token = fields.Char()
    mfa_login_token_exp = fields.Datetime()
    trusted_device_ids = fields.One2many(
        comodel_name='res.users.device',
        inverse_name='user_id',
        string='Trusted Devices',
    )

    @api.multi
    @api.constrains('mfa_enabled', 'authenticator_ids')
    def _check_enabled_with_authenticator(self):
        for record in self:
            if record.mfa_enabled and not record.authenticator_ids:
                raise ValidationError(_(
                    'You have MFA enabled but do not have any authentication'
                    ' apps/devices set up. To keep from being locked out,'
                    ' please add one before you activate this feature.'
                ))

    @api.model
    def check_credentials(self, password):
        try:
            return super(ResUsers, self).check_credentials(password)
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
                random.SystemRandom().choice(char_set) for __ in range(20)
            )

            expiration = datetime.now() + timedelta(minutes=lifetime_mins)
            record.mfa_login_token_exp = fields.Datetime.to_string(expiration)

    @api.model
    def user_from_mfa_login_token(self, token):
        if not token:
            raise MfaTokenInvalidError(_(
                'Your MFA login token is not valid. Please try again.'
            ))

        user = self.search([('mfa_login_token', '=', token)])
        user._user_from_mfa_login_token_validate()

        return user

    @api.multi
    def _user_from_mfa_login_token_validate(self):
        try:
            self.ensure_one()
        except ValueError:
            raise MfaTokenInvalidError(_(
                'Your MFA login token is not valid. Please try again.'
            ))

        token_exp = fields.Datetime.from_string(self.mfa_login_token_exp)
        if token_exp < datetime.now():
            raise MfaTokenExpiredError(_(
                'Your MFA login token has expired. Please try again.'
            ))

    @api.multi
    def validate_mfa_confirmation_code(self, confirmation_code):
        self.ensure_one()
        return self.authenticator_ids.validate_conf_code(confirmation_code)
