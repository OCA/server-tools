# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import api, fields, models

_logger = logging.getLogger(__name__)
try:
    import pyotp
except ImportError:
    _logger.debug(
        'Could not import PyOTP. Please make sure this library is available in'
        ' your environment.'
    )


class ResUsersAuthenticator(models.Model):
    _name = 'res.users.authenticator'
    _description = 'MFA App/Device'
    _sql_constraints = [(
        'user_id_name_uniq',
        'UNIQUE(user_id, name)',
        'There is already an MFA app/device with this name associated with'
        ' your account. Please pick a new name and try again.',
    )]

    name = fields.Char(
        required=True,
        readonly=True,
    )
    secret_key = fields.Char(
        required=True,
        readonly=True,
    )
    user_id = fields.Many2one(
        comodel_name='res.users',
        ondelete='cascade',
    )

    @api.multi
    @api.constrains('user_id')
    def _check_has_user(self):
        for record in self:
            if not record.user_id:
                record.unlink()

    @api.multi
    def validate_conf_code(self, confirmation_code):
        for record in self:
            totp = pyotp.TOTP(record.secret_key)
            if totp.verify(confirmation_code):
                return True

        return False
