# -*- coding: utf-8 -*-
# Copyright 2016 SYLEAM
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp.tests.common import TransactionCase


class TestOAuthProviderScope(TransactionCase):

    def setUp(self):
        super(TestOAuthProviderScope, self).setUp()
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

    def new_scope(self, vals=None):
        values = self.scope_vals
        if vals is not None:
            values.update(vals)

        return self.env['oauth.provider.scope'].create(values)

    def test_get_data_from_model_without_filter(self):
        """ Check the values returned by the get_data_for_model method when no
        filter is defined
        """
        scope = self.new_scope({'filter_id': False})

        # Check a simple call with the right model
        data = scope.get_data_for_model('res.users')
        # Check that we have multiple users (otherwise this test is useless)
        self.assertTrue(len(self.env['res.users'].search([]).ids) > 1)
        self.assertEqual(
            set(data.keys()), set(self.env['res.users'].search([]).ids))

    def test_get_data_from_model_without_filter_wrong_model(self):
        """ Check the values returned by the get_data_for_model method when no
        filter is defined
        """
        scope = self.new_scope({'filter_id': False})

        # Check a simple call with a wrong model
        data = scope.get_data_for_model('res.partner')
        self.assertEqual(data, {})

    def test_get_data_from_model_with_filter(self):
        """ Check the values returned by the get_data_for_model method when no
        res_id is supplied
        """
        scope = self.new_scope()

        # Check a simple call with the right model
        data = scope.get_data_for_model('res.users')
        self.assertEqual(data, {
            self.env.user.id: {
                'id': self.env.user.id,
                'email': self.env.user.email,
            },
        })

    def test_get_data_from_model_with_filter_wrong_model(self):
        """ Check the values returned by the get_data_for_model method when no
        res_id is supplied
        """
        scope = self.new_scope()

        # Check a simple call with a wrong model
        data = scope.get_data_for_model('res.partner')
        self.assertEqual(data, {})

    def test_get_data_from_model_with_res_id_and_no_filter(self):
        """ Check the values returned by the get_data_for_model method when a
        res_id is supplied
        """
        scope = self.new_scope({'filter_id': False})

        # Check a simple call with the right model
        data = scope.get_data_for_model('res.users', res_id=self.env.user.id)
        self.assertEqual(data, {
            'id': self.env.user.id,
            'email': self.env.user.email,
        })

    def test_get_data_from_model_with_res_id_and_no_filter_wrong_model(self):
        """ Check the values returned by the get_data_for_model method when a
        res_id is supplied
        """
        scope = self.new_scope({'filter_id': False})

        # Check a simple call with a wrong model
        data = scope.get_data_for_model(
            'res.partner', res_id=self.env.user.id + 1)
        self.assertEqual(data, {})

    def test_get_data_from_model_with_res_id(self):
        """ Check the values returned by the get_data_for_model method when a
        res_id is supplied
        """
        scope = self.new_scope()

        # Check a simple call with the right model
        data = scope.get_data_for_model('res.users', res_id=self.env.user.id)
        self.assertEqual(data, {
            'id': self.env.user.id,
            'email': self.env.user.email,
        })

    def test_get_data_from_model_with_res_id_wrong_model(self):
        """ Check the values returned by the get_data_for_model method when a
        res_id is supplied
        """
        scope = self.new_scope()

        # Check a simple call with a wrong model
        data = scope.get_data_for_model(
            'res.partner', res_id=self.env.user.id + 1)
        self.assertEqual(data, {})

    def _generate_multiple_scopes(self):
        scopes = self.new_scope()
        scopes += self.new_scope({
            'code': 'Profile',
            'field_ids': [(6, 0, [
                self.env.ref('base.field_res_users_name').id,
                self.env.ref('base.field_res_users_city').id,
                self.env.ref('base.field_res_users_country_id').id,
            ])],
        })
        scopes += self.new_scope({
            'model_id': self.env.ref('base.model_res_groups').id,
            'code': 'All groups',
            'filter_id': False,
            'field_ids': [
                (6, 0, [self.env.ref('base.field_res_groups_name').id]),
            ],
        })

        return scopes

    def test_get_data_from_model_with_multiple_scopes_empty_fields(self):
        """ Check the values returned by the get_data_for_model method when
        calling on multiple scopes
        """
        scopes = self._generate_multiple_scopes()

        # Check a simple call with the right model with empty fields
        self.env.user.city = False
        self.env.user.country_id = False
        data = scopes.get_data_for_model('res.users')
        self.assertEqual(data, {self.env.user.id: {
            'id': 1,
            'email': self.env.user.email,
            'name': self.env.user.name,
            'city': False,
            'country_id': False,
        }})

    def test_get_data_from_model_with_multiple_scopesfirst_model(self):
        """ Check the values returned by the get_data_for_model method when
        calling on multiple scopes
        """
        scopes = self._generate_multiple_scopes()

        # Check a simple call with the right model without empty fields
        country = self.env.ref('base.fr')
        self.env.user.city = 'Paris'
        self.env.user.country_id = country
        data = scopes.get_data_for_model('res.users')
        self.assertEqual(data, {self.env.user.id: {
            'id': 1,
            'email': self.env.user.email,
            'name': self.env.user.name,
            'city': self.env.user.city,
            'country_id': country.name,
        }})

    def test_get_data_from_model_with_multiple_scopes_second_model(self):
        """ Check the values returned by the get_data_for_model method when
        calling on multiple scopes
        """
        scopes = self._generate_multiple_scopes()

        # Check a simple call with another right model
        data = scopes.get_data_for_model('res.groups')
        self.assertEqual(
            set(data.keys()), set(self.env['res.groups'].search([]).ids))

    def test_get_data_from_model_with_multiple_scopes_wrong_model(self):
        """ Check the values returned by the get_data_for_model method when
        calling on multiple scopes
        """
        scopes = self._generate_multiple_scopes()

        # Check a simple call with a wrong model
        data = scopes.get_data_for_model('res.partner')
        self.assertEqual(data, {})

    def _generate_multiple_scopes_match(self):
        scopes = self.new_scope()
        scopes += self.new_scope({
            'code': 'All users',
            'filter_id': False,
        })
        scopes += self.new_scope({
            'model_id': self.env.ref('base.model_res_groups').id,
            'code': 'All groups',
            'filter_id': False,
            'field_ids': [
                (6, 0, [self.env.ref('base.field_res_groups_name').id]),
            ],
        })

        return scopes

    def test_get_data_from_model_with_all_scopes_match(self):
        """ Check the values returned by the get_data_for_model method when all
        scopes are required to match
        """
        scopes = self._generate_multiple_scopes_match()

        # Check a simple call with the right model with any scope match
        # returned records
        data = scopes.get_data_for_model('res.users')
        self.assertEqual(
            set(data.keys()), set(self.env['res.users'].search([]).ids))

    def test_get_data_from_model_with_all_scopes_match_first_model(self):
        """ Check the values returned by the get_data_for_model method when all
        scopes are required to match
        """
        scopes = self._generate_multiple_scopes_match()

        # Check a simple call with the right model with all scopes required to
        # match returned records
        data = scopes.get_data_for_model('res.users', all_scopes_match=True)
        self.assertEqual(data, {self.env.user.id: {
            'id': 1,
            'email': self.env.user.email,
        }})

    def test_get_data_from_model_with_all_scopes_match_second_model(self):
        """ Check the values returned by the get_data_for_model method when all
        scopes are required to match
        """
        scopes = self._generate_multiple_scopes_match()

        # Check a simple call with another right model
        data = scopes.get_data_for_model('res.groups')
        self.assertEqual(
            set(data.keys()), set(self.env['res.groups'].search([]).ids))

    def test_get_data_from_model_with_all_scopes_match_wrong_model(self):
        """ Check the values returned by the get_data_for_model method when all
        scopes are required to match
        """
        scopes = self._generate_multiple_scopes_match()

        # Check a simple call with a wrong model
        data = scopes.get_data_for_model('res.partner')
        self.assertEqual(data, {})
