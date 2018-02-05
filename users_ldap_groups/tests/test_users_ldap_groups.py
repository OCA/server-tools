# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from mock import Mock, patch
from odoo.tests.common import TransactionCase


@patch('ldap.initialize', return_value=Mock(
    search_st=Mock(return_value=[
        ('cn=hello', {'name': ['hello', 'hello2']})
    ]),
))
class TestUsersLdapGroups(TransactionCase):
    def test_users_ldap_groups(self, ldap_initialize):
        # _login does its work in a new cursor, so we need one too
        with self.env.registry.cursor() as cr:
            env = self.env(cr=cr)
            group_contains = env['res.groups'].create({'name': 'contains'})
            group_equals = env['res.groups'].create({'name': 'equals'})
            group_query = env['res.groups'].create({'name': 'query'})
            env.ref('base.main_company').write({'ldaps': [(0, 0, {
                'ldap_server': 'localhost',
                'ldap_filter': '(&(objectClass=*),(uid=%s))',
                'ldap_base': 'base',
                'only_ldap_groups': True,
                'group_mapping_ids': [
                    (0, 0, {
                        'ldap_attribute': 'name',
                        'operator': 'contains',
                        'value': 'hello3',
                        'group_id': env.ref('base.group_system').id,
                    }),
                    (0, 0, {
                        'ldap_attribute': 'name',
                        'operator': 'contains',
                        'value': 'hello2',
                        'group_id': group_contains.id,
                    }),
                    (0, 0, {
                        'ldap_attribute': 'name',
                        'operator': 'equals',
                        'value': 'hello',
                        'group_id': group_equals.id,
                    }),
                    (0, 0, {
                        'ldap_attribute': '',
                        'operator': 'query',
                        'value': 'is not run because of patching',
                        'group_id': group_query.id,
                    }),
                ],
            })]})

        self.env['res.users']._login(self.env.cr.dbname, 'demo', 'wrong')
        with self.env.registry.cursor() as cr:
            env = self.env(cr=cr)
            demo_user = env.ref('base.user_demo')
            # this asserts group mappings from demo data
            groups = demo_user.groups_id
            self.assertIn(group_contains, groups)
            self.assertNotIn(group_equals, groups)
            self.assertIn(group_query, groups)
            self.assertNotIn(env.ref('base.group_system'), groups)
            # clean up
            env.ref('base.main_company').write({'ldaps': [(6, False, [])]})
