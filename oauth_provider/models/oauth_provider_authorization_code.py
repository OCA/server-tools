# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields


class OAuthProviderAuthorizationCode(models.Model):
    _name = 'oauth.provider.authorization.code'
    _description = 'OAuth Provider Authorization Code'
    _rec_name = 'code'

    code = fields.Char(required=True, help='Name of the authorization code.')
    client_id = fields.Many2one(
        comodel_name='oauth.provider.client', string='Client', required=True,
        help='Client associated to this authorization code.')
    user_id = fields.Many2one(
        comodel_name='res.users', string='User', required=True,
        help='User associated to this authorization code.')
    redirect_uri_id = fields.Many2one(
        comodel_name='oauth.provider.redirect.uri', string='Redirect URI',
        required=True,
        help='Redirect URI associated to this authorization code.')
    scope_ids = fields.Many2many(
        comodel_name='oauth.provider.scope', string='Scopes',
        help='Scopes allowed by this authorization code.')
    active = fields.Boolean(
        default=True, help='When unchecked, the code is invalidated.')

    _sql_constraints = [
        ('code_client_id_unique', 'UNIQUE (code, client_id)',
         'The authorization code must be unique per client !'),
    ]
