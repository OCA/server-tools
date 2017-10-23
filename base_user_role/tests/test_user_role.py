# Copyright 2014 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import fields
from odoo.tests.common import TransactionCase


class TestUserRole(TransactionCase):

    def setUp(self):
        super(TestUserRole, self).setUp()
        self.user_model = self.env['res.users']
        self.role_model = self.env['res.users.role']

        self.user_id = self.user_model.create(
            {'name': "USER TEST (ROLES)", 'login': 'user_test_roles'})

        # ROLE_1
        self.group_user_id = self.env.ref('base.group_user')
        self.group_no_one_id = self.env.ref('base.group_no_one')
        vals = {
            'name': "ROLE_1",
            'implied_ids': [
                (6, 0, [self.group_user_id.id, self.group_no_one_id.id])],
        }
        self.role1_id = self.role_model.create(vals)

        # ROLE_2
        self.group_multi_currency_id = self.env.ref(
            'base.group_multi_currency')
        self.group_settings_id = self.env.ref('base.group_system')
        vals = {
            'name': "ROLE_2",
            'implied_ids': [
                (6, 0, [self.group_multi_currency_id.id,
                        self.group_settings_id.id])],
        }
        self.role2_id = self.role_model.create(vals)

    def test_role_1(self):
        self.user_id.write(
            {'role_line_ids': [(0, 0, {'role_id': self.role1_id.id})]})
        user_group_ids = sorted(set(
            [group.id for group in self.user_id.groups_id]))
        role_group_ids = self.role1_id.trans_implied_ids.ids
        role_group_ids.append(self.role1_id.group_id.id)
        role_group_ids = sorted(set(role_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)

    def test_role_2(self):
        self.user_id.write(
            {'role_line_ids': [(0, 0, {'role_id': self.role2_id.id})]})
        user_group_ids = sorted(set(
            [group.id for group in self.user_id.groups_id]))
        role_group_ids = self.role2_id.trans_implied_ids.ids
        role_group_ids.append(self.role2_id.group_id.id)
        role_group_ids = sorted(set(role_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)

    def test_role_1_2(self):
        self.user_id.write(
            {'role_line_ids': [
                (0, 0, {'role_id': self.role1_id.id}),
                (0, 0, {'role_id': self.role2_id.id}),
            ]})
        user_group_ids = sorted(set(
            [group.id for group in self.user_id.groups_id]))
        role1_group_ids = self.role1_id.trans_implied_ids.ids
        role1_group_ids.append(self.role1_id.group_id.id)
        role2_group_ids = self.role2_id.trans_implied_ids.ids
        role2_group_ids.append(self.role2_id.group_id.id)
        role_group_ids = sorted(set(role1_group_ids + role2_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)

    def test_role_1_2_with_dates(self):
        today_str = fields.Date.today()
        today = fields.Date.from_string(today)
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = fields.Date.to_string(yesterday)
        self.user_id.write(
            {'role_line_ids': [
                # Role 1 should be enabled
                (0, 0, {'role_id': self.role1_id.id, 'date_from': today_str}),
                # Role 2 should be disabled
                (0, 0,
                 {'role_id': self.role2_id.id, 'date_to': yesterday_str}),
            ]})
        user_group_ids = sorted(set(
            [group.id for group in self.user_id.groups_id]))
        role1_group_ids = self.role1_id.trans_implied_ids.ids
        role1_group_ids.append(self.role1_id.group_id.id)
        role_group_ids = sorted(set(role1_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)
