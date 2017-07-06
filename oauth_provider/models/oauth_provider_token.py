# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, api, fields, exceptions, _


class OAuthProviderToken(models.Model):
    _name = 'oauth.provider.token'
    _description = 'OAuth Provider Token'
    _rec_name = 'token'

    token = fields.Char(required=True, help='The token itself.')
    token_type = fields.Selection(
        selection=[('Bearer', 'Bearer')], required=True, default='Bearer',
        help='Type of token stored. Currently, only the bearer token type is '
        'available.')
    refresh_token = fields.Char(
        help='The refresh token, if applicable.')
    client_id = fields.Many2one(
        comodel_name='oauth.provider.client', string='Client', required=True,
        help='Client associated to this token.')
    user_id = fields.Many2one(
        comodel_name='res.users', string='User', required=True,
        help='User associated to this token.')
    scope_ids = fields.Many2many(
        comodel_name='oauth.provider.scope', string='Scopes',
        help='Scopes allowed by this token.')
    expires_at = fields.Datetime(
        required=True, help='Expiration time of the token.')
    active = fields.Boolean(
        compute='_compute_active', search='_search_active',
        help='A token is active only if it has not yet expired.')

    _sql_constraints = [
        ('token_unique', 'UNIQUE (token, client_id)',
         'The token must be unique per client !'),
        ('refresh_token_unique', 'UNIQUE (refresh_token, client_id)',
         'The refresh token must be unique per client !'),
    ]

    @api.multi
    def _compute_active(self):
        for token in self:
            token.active = fields.Datetime.now() < token.expires_at

    @api.model
    def _search_active(self, operator, operand):
        domain = []
        if operator == 'in':
            if True in operand:
                domain += self._search_active('=', True)
            if False in operand:
                domain += self._search_active('=', False)
            if len(domain) > 1:
                domain = [(1, '=', 1)]
        elif operator == 'not in':
            if True in operand:
                domain += self._search_active('!=', True)
            if False in operand:
                domain += self._search_active('!=', False)
            if len(domain) > 1:
                domain = [(0, '=', 1)]
        elif operator in ('=', '!='):
            operators = {
                ('=', True): '>',
                ('=', False): '<=',
                ('!=', False): '>',
                ('!=', True): '<=',
            }
            domain = [('expires_at', operators[operator, operand],
                       fields.Datetime.now())]
        else:
            raise exceptions.UserError(
                _('Invalid operator {operator} for  field active!').format(
                    operator=operator))

        return domain

    @api.multi
    def generate_user_id(self):
        """ Generates a unique user identifier for this token """
        self.ensure_one()

        return self.client_id.generate_user_id(self.user_id)

    @api.multi
    def get_data_for_model(self, model, res_id=None, all_scopes_match=False):
        """ Returns the data of the accessible records of the requested model,

        Data are returned depending on the allowed scopes for the token
        If the all_scopes_match argument is set to True, return only records
        allowed by all token's scopes
        """
        self.ensure_one()

        # Retrieve records allowed from all scopes
        return self.sudo(user=self.user_id).scope_ids.get_data_for_model(
            model, res_id=res_id, all_scopes_match=all_scopes_match)
