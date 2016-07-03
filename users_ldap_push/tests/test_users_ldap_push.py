# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV <http://therp.nl>.
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
import ldap
from openerp.tests.common import TransactionCase


class FakeLdapConnection(object):
    def __init__(self):
        self.entries = {}

    def simple_bind_s(self, dn, passwd):
        pass

    def add_s(self, dn, modlist):
        self.entries[dn] = modlist

    def search_s(self, dn, scope, ldap_filter, attributes):
        if dn in self.entries:
            return [(dn, dict(self.entries[dn]))]
        return None

    def modify_s(self, dn, modlist):
        if dn not in self.entries:
            raise ldap.NO_SUCH_OBJECT()
        for operation, attribute, value in modlist:
            if operation == ldap.MOD_ADD:
                self.entries[dn].append((attribute, value))
                continue

    def unbind_s(self):
        pass


class TestUsersLdapPush(TransactionCase):
    def test_users_ldap_push(self):
        company = self.env['res.company'].create({
            'name': 'testcompany',
            'ldaps': [(0, 0, {
                'ldap_base': 'dc=test',
                'ldap_filter': '(uid=%s)',
                'create_ldap_entry_field_mappings': [
                    (
                        0, 0, {
                            'field_id':
                            self.env.ref('base.field_res_users_login').id,
                            'attribute': 'userid',
                            'use_for_dn': True,
                        },
                    ),
                    (
                        0, 0, {
                            'field_id':
                            self.env.ref('base.field_res_users_name').id,
                            'attribute': 'sn',
                        },
                    ),
                ],
            })],
        })
        fake_ldap = FakeLdapConnection()
        self.env['res.company.ldap']._patch_method(
            'connect', lambda x, y: fake_ldap)
        user = self.env['res.users'].create({
            'name': 'testuser',
            'login': 'testuser',
            'company_ids': [(6, 0, company.ids)],
            'company_id': company.id,
            'is_ldap_user': False,
        })
        self.assertFalse(user.ldap_entry_dn)
        user.unlink()
        user = self.env['res.users'].create({
            'name': 'testuser',
            'login': 'testuser',
            'company_ids': [(6, 0, company.ids)],
            'company_id': company.id,
            'is_ldap_user': True,
        })
        self.assertTrue(fake_ldap.entries[user.ldap_entry_dn])
        self.assertEqual(
            dict(fake_ldap.entries[user.ldap_entry_dn])['userid'],
            [user.login])
        user.partner_id.write({'name': 'testuser2'})
        self.assertTrue([
            v for a, v in fake_ldap.entries[user.ldap_entry_dn]
            if v == ['testuser2']
        ])
