# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import models, api, fields, exceptions, _


class OauthProviderToken(models.Model):
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

    @property
    @api.multi
    def user_scopes(self):
        self.ensure_one()
        return self.sudo(user=self.user_id).scope_ids

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
    def get_data(self, model, record_ids=None, all_scopes_match=False,
                 domain=None):
        """ Returns the data of the accessible records of the requested model.

        Args:
            model (str): Name of the model to operate on.
            record_ids (int or list of ints): ID of record to find. Will
                only return this record, if defined.
            all_scopes_match (bool): True to filter out records that do not
                match all of the scopes in the current recordset.
            domain (list of tuples, optional): Domain to append to the
                `filter_domain` that is defined in the scope.

        Returns:
            dict: If `record_ids` is defined, this will be the scoped data for
                the appropriate record (or empty dict if no match). Otherwise,
                this will be a dictionary of scoped record data, keyed by
                record ID.

        Data are returned depending on the allowed scopes for the token
        If the all_scopes_match argument is set to True, return only records
        allowed by all token's scopes
        """
        return self.user_scopes.get_data(
            model,
            record_ids,
            all_scopes_match=all_scopes_match,
            domain=domain,
        )

    @api.multi
    def create_record(self, model, vals):
        return self.user_scopes.create_record(model, vals)

    @api.multi
    def write_record(self, model, record_ids, vals):
        scopes = self.user_scopes
        # Browse using the scope env, which is in the token's user
        records = scopes.env[model].browse(record_ids)
        return scopes.write_record(records, vals)

    @api.multi
    def delete_record(self, model, record_ids):
        scopes = self.user_scopes
        # Browse using the scope env, which is in the token's user
        records = scopes.env[model].browse(record_ids)
        return scopes.delete_record(records)
