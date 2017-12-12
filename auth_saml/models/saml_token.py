# -*- coding: utf-8 -*-

import logging
from openerp import fields
from openerp import models

_logger = logging.getLogger(__name__)


class SamlToken(models.Model):
    _name = "auth_saml.token"
    _rec_name = "user_id"

    saml_provider_id = fields.Many2one(
        'auth.saml.provider',
        string='SAML Provider that issued the token',
    )
    user_id = fields.Many2one(
        'res.users',
        string="User",
        # we want the token to be destroyed if the corresponding res.users
        # is deleted
        ondelete="cascade"
    )
    saml_access_token = fields.Char(
        'Current SAML token for this user',
        help="The current SAML token in use",
    )
