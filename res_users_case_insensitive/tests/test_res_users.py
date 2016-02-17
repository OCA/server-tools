# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestResUsers(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestResUsers, self).setUp(*args, **kwargs)
        self.login = 'LasLabs@ExAmPlE.CoM'
        self.partner_vals = {
            'name': 'Partner',
            'is_company': False,
            'email': self.login,
        }
        self.vals = {
            'name': 'User',
            'login': self.login,
            'password': 'password',
        }
        self.model_obj = self.env['res.users']

    def _new_record(self, ):
        partner_id = self.env['res.partner'].create(self.partner_vals)
        self.vals['partner_id'] = partner_id.id
        return self.model_obj.create(self.vals)

    def test_login_is_lowercased_on_create(self, ):
        rec_id = self._new_record()
        self.assertEqual(
            self.login.lower(), rec_id.login,
            'Login was not lowercased when saved to db.',
        )

    def test_login_is_lowercased_on_write(self, ):
        rec_id = self._new_record()
        rec_id.write({'login': self.login})
        self.assertEqual(
            self.login.lower(), rec_id.login,
            'Login was not lowercased when saved to db.',
        )

    def test_login_search_is_lowercased(self, ):
        rec_id = self._new_record()
        res_id = self.model_obj.search([('login', '=', self.login.upper())])
        res = res_id.id if res_id else False
        self.assertEqual(
            rec_id.id, res,
            'Search for login with uppercase chars did not yield results.',
        )
