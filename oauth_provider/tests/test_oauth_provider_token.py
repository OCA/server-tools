# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta
from openerp import fields, exceptions
from openerp.tests.common import TransactionCase


class TestOAuthProviderToken(TransactionCase):

    def setUp(self):
        super(TestOAuthProviderToken, self).setUp()
        self.client = self.env['oauth.provider.client'].create({
            'name': 'Client',
            'identifier': 'client',
        })
        self.token_vals = {
            'user_id': self.env.user.id,
            'client_id': self.client.id,
            'token': 'token',
            'expires_at': fields.Datetime.now(),
        }
        self.filter = self.env['ir.filters'].create({
            'name': 'Current user',
            'model_id': 'res.users',
            'domain': "[('id', '=', uid)]",
        })
        self.scope_vals = {
            'name': 'Scope',
            'code': 'scope',
            'description': 'Description of the scope',
            'model_id': self.env.ref('base.model_res_users').id,
            'filter_id': self.filter.id,
            'field_ids': [
                (6, 0, [self.env.ref('base.field_res_users_email').id]),
            ],
        }

    def new_token(self, vals=None):
        values = self.token_vals
        if vals is not None:
            values.update(vals)

        return self.env['oauth.provider.token'].create(values)

    def new_scope(self, vals=None):
        values = self.scope_vals
        if vals is not None:
            values.update(vals)

        return self.env['oauth.provider.scope'].create(values)

    def test_inactive(self):
        """ Check the value of the active field, for an expired token """
        not_expired = datetime.now() + timedelta(days=1)
        token = self.new_token(vals={
            'token': 'Active',
            'expires_at': fields.Datetime.to_string(not_expired),
        })
        self.assertEqual(token.active, True)

    def test_active(self):
        """ Check the value of the active field, for a not expired token """
        expired = datetime.now() - timedelta(minutes=1)
        token = self.new_token(vals={
            'token': 'Not active',
            'expires_at': fields.Datetime.to_string(expired),
        })
        self.assertEqual(token.active, False)

    def _generate_tokens_for_active_search(self):
        not_expired = datetime.now() + timedelta(days=1)
        not_expired_tokens = self.new_token(vals={
            'token': 'Not expired',
            'expires_at': fields.Datetime.to_string(not_expired),
        })
        not_expired_tokens += not_expired_tokens.copy(default={
            'token': 'Other not expired',
        })

        expired = datetime.now() - timedelta(minutes=1)
        expired_tokens = self.new_token(vals={
            'token': 'Expired',
            'expires_at': fields.Datetime.to_string(expired),
        })
        expired_tokens += expired_tokens.copy(default={
            'token': 'Other expired',
        })

        return expired_tokens, not_expired_tokens

    def test_search_empty_domain(self):
        """ Check the results of searching tokens with an empty domain

        Only active tokens should be returned
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([]), not_expired_tokens)

    def test_active_search_equal_true(self):
        """ Check the results of searching tokens with explicit active = True domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', '=', True),
        ]), not_expired_tokens)

    def test_active_search_equal_false(self):
        """ Check the results of searching tokens with active = False domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', '=', False),
        ]), expired_tokens)

    def test_active_search_not_equal_true(self):
        """ Check the results of searching tokens with active != True domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', '!=', True),
        ]), expired_tokens)

    def test_active_search_not_equal_false(self):
        """ Check the results of searching tokens with active != False domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', '!=', False),
        ]), not_expired_tokens)

    def test_active_search_in_true(self):
        """ Check the results of searching tokens with active in (True,) domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', 'in', (True,)),
        ]), not_expired_tokens)

    def test_active_search_in_false(self):
        """ Check the results of searching tokens with active in (False,) domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', 'in', (False,)),
        ]), expired_tokens)

    def test_active_search_not_in_true(self):
        """ Check the results of searching tokens with active not in (True,) domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', 'not in', (True,)),
        ]), expired_tokens)

    def test_active_search_not_in_false(self):
        """ Check the results of searching tokens with active not in (False,) domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', 'not in', (False,)),
        ]), not_expired_tokens)

    def test_active_search_in_true_false(self):
        """ Check the results of searching tokens with active in (True, False) domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', 'in', (True, False)),
        ]), not_expired_tokens + expired_tokens)

    def test_active_search_not_in_true_false(self):
        """ Check the results of searching tokens with active notin (True,False) domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        self.assertEqual(token_obj.search([
            ('active', 'not in', (True, False)),
        ]), token_obj)

    def test_active_search_invalid_operator(self):
        """ Check the results of searching tokens with an invalid operatr in domain
        """
        token_obj = self.env['oauth.provider.token']
        expired_tokens, not_expired_tokens = \
            self._generate_tokens_for_active_search()

        with self.assertRaises(exceptions.UserError):
            token_obj.search([('active', '>', True)])

    def test_get_data_from_model_with_at_least_one_scope_matching(self):
        """ Check the values returned by the get_data_for_model method with
        at least one scope matching the data
        """
        scopes = self.new_scope()
        scopes += self.new_scope({
            'code': 'All users',
            'filter_id': False,
        })
        token = self.new_token(vals={
            'scope_ids': [(6, 0, scopes.ids)],
        })

        # Check a simple call with the right model with empty fields
        data = token.get_data_for_model('res.users')
        self.assertEqual(
            sorted(data.keys()), sorted(self.env['res.users'].search([]).ids))

    def test_get_data_from_model_with_all_scopes_matching(self):
        """ Check the values returned by the get_data_for_model method with
        all scopes required to match the data
        """
        scopes = self.new_scope()
        scopes += self.new_scope({
            'code': 'All users',
            'filter_id': False,
        })
        token = self.new_token(vals={
            'scope_ids': [(6, 0, scopes.ids)],
        })

        # Check a simple call with the right model without empty fields
        data = token.get_data_for_model('res.users', all_scopes_match=True)
        self.assertEqual(data, {self.env.user.id: {
            'id': 1,
            'email': self.env.user.email,
        }})

    def test_get_data_from_model_with_no_scope_matching(self):
        """ Check the values returned by the get_data_for_model method with
        an unauthorized model
        """
        token = self.new_token()

        # Check a simple call with a wrong model
        data = token.get_data_for_model('res.partner')
        self.assertEqual(data, {})
