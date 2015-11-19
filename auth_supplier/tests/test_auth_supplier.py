# -*- coding: utf-8 -*-
# (c) 2015 Antiun Ingeniería S.L. - Sergio Teruel
# (c) 2015 Antiun Ingeniería S.L. - Carlos Dauden
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from openerp.tests.common import TransactionCase


class TestSAuthSupplier(TransactionCase):

    def setUp(self):
        super(TestSAuthSupplier, self).setUp()
        ir_config_parameter = self.env['ir.config_parameter']
        ir_config_parameter.set_param('auth_signup.allow_uninvited', 'True')

    def test_user_signup(self):
        values = {
            'login': 'test@test.com',
            'name': 'test',
            'password': '1234',
            'account_type': 'supplier'
        }
        user_obj = self.env['res.users']
        user = user_obj.browse(user_obj._signup_create_user(values))
        self.assertTrue(user.partner_id.supplier)
