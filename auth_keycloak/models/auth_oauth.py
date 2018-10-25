# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
from odoo import fields, models, api


class OAuthProvider(models.Model):
    _inherit = 'auth.oauth.provider'

    client_secret = fields.Char()
    users_endpoint = fields.Char(
        help='User endpoint',
        placeholder='http://keycloak.mycompany.com'
                    '/auth/admin/realms/{realm}/users',
        required=False,
    )
    superuser = fields.Char(
        help='A super power user that is able to CRUD users on KC.',
        placeholder='admin',
        required=False,
    )
    superuser_pwd = fields.Char(
        help='"Superuser" user password',
        placeholder='I hope is not "admin"',
        required=False,
    )
    users_management_enabled = fields.Boolean(
        compute='_compute_users_management_enabled'
    )

    @api.depends(
        'enabled',
        'users_endpoint',
        'superuser',
        'superuser_pwd',
    )
    def _compute_users_management_enabled(self):
        for item in self:
            item.users_management_enabled = all([
                item.enabled,
                item.users_endpoint,
                item.superuser,
                item.superuser_pwd,
            ])
