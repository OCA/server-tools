# -*- encoding: utf-8 -*-
__author__ = 'faide'


import logging
from openerp.osv import osv, fields

_logger = logging.getLogger(__name__)


class saml_token(osv.Model):
    _name = "auth_saml.token"
    _rec_name = "user_id"

    _columns = {
        'saml_provider_id': fields.many2one(
            'auth.saml.provider',
            string='SAML Provider that issued the token',
        ),
        'user_id': fields.many2one(
            'res.users',
            string="User",
            # we want the token to be destroyed if the corresponding res.users
            # is deleted
            ondelete="cascade"
        ),
        'saml_access_token': fields.char(
            'Current SAML token for this user',
            help="The current SAML token in use",
        ),
    }
