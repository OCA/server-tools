
# -*- coding: utf-8 -*-
# Copyright 2016 Florent de Labarre
# Copyright 2017 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import uuid
from odoo import api, fields, models, exceptions
from odoo.addons import base


base.res.res_users.USER_PRIVATE_FIELDS.\
    append('oauth_master_uuid')


class ResUsers(models.Model):
    _inherit = 'res.users'

    oauth_access_token_ids = fields.One2many(
        comodel_name='auth.oauth.multi.token',
        inverse_name='user_id',
        string='OAuth tokens',
        copy=False
    )
    oauth_access_max_token = fields.Integer(
        string='Max number of simultaneous connections',
        default=10,
        required=True
    )
    oauth_master_uuid = fields.Char(
        string='Master UUID',
        copy=False,
        readonly=True,
        required=True,
        default=lambda self: self._generate_oauth_master_uuid(),
    )

    def _generate_oauth_master_uuid(self):
        return uuid.uuid4().hex

    @property
    def multi_token_model(self):
        return self.env['auth.oauth.multi.token']

    @api.model
    def _auth_oauth_signin(self, provider, validation, params):
        """Override to handle sign-in with multi token."""
        res = super(ResUsers, self)._auth_oauth_signin(
            provider, validation, params)

        oauth_uid = validation['user_id']
        # Lookup for user by oauth uid and provider
        user = self.search([
            ('oauth_uid', '=', oauth_uid),
            ('oauth_provider_id', '=', provider)]
        )
        if not user:
            raise exceptions.AccessDenied()
        user.ensure_one()
        # user found and unique: create a token
        self.multi_token_model.create({
            'user_id': user.id,
            'oauth_access_token': params['access_token'],
            'active_token': True,
        })
        return res

    @api.multi
    def action_oauth_clear_token(self):
        """Inactivate current user tokens."""
        self.mapped('oauth_access_token_ids')._oauth_clear_token()
        for res in self:
            res.oauth_master_uuid = self._generate_oauth_master_uuid()

    @api.model
    def check_credentials(self, password):
        """Override to check credentials against multi tokens."""
        try:
            return super(ResUsers, self).check_credentials(password)
        except exceptions.AccessDenied:
            res = self.multi_token_model.sudo().search([
                ('user_id', '=', self.env.uid),
                ('oauth_access_token', '=', password),
                ('active_token', '=', True),
            ])
            if not res:
                raise

    def _get_session_token_fields(self):
        res = super(ResUsers, self)._get_session_token_fields()
        res.remove('oauth_access_token')
        return res | {'oauth_master_uuid'}
