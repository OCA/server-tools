# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Dave Lasley <dave@laslabs.com>
#    Copyright: 2016-TODAY LasLabs, Inc. [https://laslabs.com]
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests.common import TransactionCase


class TestResUsers(TransactionCase):

    def setUp(self, *args, **kwargs):
        result = super(SomethingCase, self).setUp(*args, **kwargs)
        self.login = 'TeSt@ExAmPlE.CoM'
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
        return self.model_obj.create(self.vals)

    def test_login_is_lowercased_on_save(self, ):
        rec_id = self._new_record()
        self.assertEqual(
            self.login.lower(), rec_id.login,
            'Login was not lowercased when saved to cache',
        )
