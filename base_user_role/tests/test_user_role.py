# -*- coding: utf-8 -*-
# Copyright 2014 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tests.common import TransactionCase


class TestUserRole(TransactionCase):

    def setUp(self):
        super(TestUserRole, self).setUp()
        self.imd_model = self.registry('ir.model.data')
        self.user_model = self.registry('res.users')
        self.role_model = self.registry('res.users.role')

        self.user_id = self.user_model.create(
            self.cr, self.uid,
            {'name': u"USER TEST (ROLES)", 'login': 'user_test_roles'})

        # ROLE_1
        self.group_user_id = self.imd_model.get_object_reference(
            self.cr, self.uid, 'base', 'group_user')[1]
        self.group_no_one_id = self.imd_model.get_object_reference(
            self.cr, self.uid, 'base', 'group_no_one')[1]
        vals = {
            'name': u"ROLE_1",
            'implied_ids': [6, 0, [self.group_user_id, self.group_no_one_id]],
        }
        self.role1_id = self.role_model.create(self.cr, self.uid, vals)

        # ROLE_2
        self.group_multi_currency_id = self.imd_model.get_object_reference(
            self.cr, self.uid, 'base', 'group_multi_currency')[1]
        self.group_sale_manager_id = self.imd_model.get_object_reference(
            self.cr, self.uid, 'base', 'group_sale_manager')[1]
        vals = {
            'name': u"ROLE_2",
            'implied_ids': [6, 0, [self.group_multi_currency_id,
                                   self.group_sale_manager_id]],
        }
        self.role2_id = self.role_model.create(self.cr, self.uid, vals)

    def test_role_1(self):
        role1 = self.role_model.browse(self.cr, self.uid, self.role1_id)
        self.user_model.write(
            self.cr, self.uid, [self.user_id],
            {'role_line_ids': [(0, 0, {'role_id': self.role1_id})]})
        user = self.user_model.browse(self.cr, self.uid, self.user_id)
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        role_group_ids = role1.implied_ids.ids
        role_group_ids.append(role1.group_id.id)
        role_group_ids = sorted(set(role_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)

    def test_role_2(self):
        role2 = self.role_model.browse(self.cr, self.uid, self.role2_id)
        self.user_model.write(
            self.cr, self.uid, [self.user_id],
            {'role_line_ids': [(0, 0, {'role_id': self.role2_id})]})
        user = self.user_model.browse(self.cr, self.uid, self.user_id)
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        role_group_ids = role2.implied_ids.ids
        role_group_ids.append(role2.group_id.id)
        role_group_ids = sorted(set(role_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)

    def test_role_1_2(self):
        role1 = self.role_model.browse(self.cr, self.uid, self.role1_id)
        role2 = self.role_model.browse(self.cr, self.uid, self.role2_id)
        self.user_model.write(
            self.cr, self.uid, [self.user_id],
            {'role_line_ids': [
                (0, 0, {'role_id': self.role1_id}),
                (0, 0, {'role_id': self.role2_id}),
            ]})
        user = self.user_model.browse(self.cr, self.uid, self.user_id)
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        role1_group_ids = role1.implied_ids.ids
        role1_group_ids.append(role1.group_id.id)
        role2_group_ids = role2.implied_ids.ids
        role2_group_ids.append(role2.group_id.id)
        role_group_ids = sorted(set(role1_group_ids + role2_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)

    def test_role_1_2_with_dates(self):
        role1 = self.role_model.browse(self.cr, self.uid, self.role1_id)
        today = datetime.date.today()
        today_str = today.strftime(DEFAULT_SERVER_DATE_FORMAT)
        yesterday = today - datetime.timedelta(days=1)
        yesterday_str = yesterday.strftime(DEFAULT_SERVER_DATE_FORMAT)
        self.user_model.write(
            self.cr, self.uid, [self.user_id],
            {'role_line_ids': [
                # Role 1 should be enabled
                (0, 0, {'role_id': self.role1_id, 'date_from': today_str}),
                # Role 2 should be disabled
                (0, 0, {'role_id': self.role2_id, 'date_to': yesterday_str}),
            ]})
        user = self.user_model.browse(self.cr, self.uid, self.user_id)
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        role1_group_ids = role1.implied_ids.ids
        role1_group_ids.append(role1.group_id.id)
        role_group_ids = sorted(set(role1_group_ids))
        self.assertEqual(user_group_ids, role_group_ids)

    def test_role_unlink(self):
        # Get role1 groups
        role1 = self.role_model.browse(self.cr, self.uid, self.role1_id)
        role1_group_ids = role1.implied_ids.ids
        role1_group_ids.append(role1.group_id.id)
        role1_group_ids = sorted(set(role1_group_ids))
        # Get role2
        role2 = self.role_model.browse(self.cr, self.uid, self.role2_id)
        # Configure the user with role1 and role2
        self.user_model.write(
            self.cr, self.uid, [self.user_id],
            {'role_line_ids': [
                (0, 0, {'role_id': self.role1_id}),
                (0, 0, {'role_id': self.role2_id}),
            ]})
        user = self.user_model.browse(self.cr, self.uid, self.user_id)
        # Remove role2
        role2.unlink()
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        self.assertEqual(user_group_ids, role1_group_ids)
        # Remove role1
        role1.unlink()
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        self.assertEqual(user_group_ids, [])

    def test_role_line_unlink(self):
        # Get role1 groups
        role1 = self.role_model.browse(self.cr, self.uid, self.role1_id)
        role1_group_ids = role1.implied_ids.ids
        role1_group_ids.append(role1.group_id.id)
        role1_group_ids = sorted(set(role1_group_ids))
        # Configure the user with role1 and role2
        self.user_model.write(
            self.cr, self.uid, [self.user_id],
            {'role_line_ids': [
                (0, 0, {'role_id': self.role1_id}),
                (0, 0, {'role_id': self.role2_id}),
            ]})
        user = self.user_model.browse(self.cr, self.uid, self.user_id)
        # Remove role2 from the user
        user.role_line_ids.filtered(
            lambda l: l.role_id.id == self.role2_id).unlink()
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        self.assertEqual(user_group_ids, role1_group_ids)
        # Remove role1 from the user
        user.role_line_ids.filtered(
            lambda l: l.role_id.id == self.role1_id).unlink()
        user_group_ids = sorted(set([group.id for group in user.groups_id]))
        self.assertEqual(user_group_ids, [])
