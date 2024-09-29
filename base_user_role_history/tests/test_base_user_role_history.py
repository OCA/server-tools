# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).µ

from datetime import date, timedelta

from odoo import fields
from odoo.tests.common import SavepointCase


class TestBaseUserRoleHistory(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestBaseUserRoleHistory, cls).setUpClass()

        # MODELS

        cls.history_line_model = cls.env['base.user.role.line.history']
        cls.role_model = cls.env['res.users.role']
        cls.user_model = cls.env['res.users']

        # INSTANCE

        cls.user_01 = cls.user_model.search([
            ('id', '!=', cls.env.user.id)
        ], limit=1)
        cls.role_01 = cls.role_model.create({
            'name': "Role test 01",
        })

    def test_write_role_lines_on_user(self):
        """
        Data :
            - user with no role
        Test case :
            1) add a role
            2) role modification with dates
            3) role modification with no change
            4) role unlink
        Expected results :
            1) new role history line created with performed_action == 'add'
            2) new role history line created with performed_action == 'edit'
            3) no new role history line created
            4) new role history line created with performed_action == 'unlink'
        """
        # 1
        history_lines_0 = self.history_line_model.search([
            ('user_id', '=', self.user_01.id)
        ])
        self.assertFalse(history_lines_0)
        self.user_01.write({
            'role_line_ids': [
                (0, 0, {
                    'role_id': self.role_01.id
                })
            ]
        })
        history_lines_1 = self.history_line_model.search([
            ('user_id', '=', self.user_01.id)
        ])
        self.assertTrue(history_lines_1)
        self.assertEqual(len(history_lines_1), 1)
        self.assertEqual(history_lines_1.performed_action, 'add')
        self.assertFalse(history_lines_1.old_role_id)
        self.assertEqual(history_lines_1.new_role_id, self.role_01)
        # 2
        self.user_01.write({
            'role_line_ids': [
                (1, self.user_01.role_line_ids[0].id, {
                    'date_from': date.today(),
                    'date_to': date.today() + timedelta(days=5),
                })
            ]
        })
        history_lines_2 = self.history_line_model.search([
            ('user_id', '=', self.user_01.id),
            ('id', 'not in', history_lines_1.ids)
        ])
        self.assertTrue(history_lines_2)
        self.assertEqual(len(history_lines_2), 1)
        self.assertEqual(history_lines_2.performed_action, 'edit')
        self.assertEqual(history_lines_2.old_role_id, self.role_01)
        self.assertEqual(history_lines_2.new_role_id, self.role_01)
        self.assertFalse(history_lines_2.old_date_from)
        self.assertEqual(history_lines_2.new_date_from,
                         fields.Date.to_string(date.today()))
        self.assertFalse(history_lines_2.old_date_to)
        self.assertEqual(history_lines_2.new_date_to,
                         fields.Date.to_string(
                             date.today() + timedelta(days=5)))
        self.user_01.write({
            'role_line_ids': [(1, self.user_01.role_line_ids[0].id, {})]
        })
        history_lines_3 = self.history_line_model.search([
            ('user_id', '=', self.user_01.id),
            ('id', 'not in', (history_lines_1 | history_lines_2).ids)
        ])
        self.assertFalse(history_lines_3)
        # 4
        self.user_01.write({
            'role_line_ids': [(2, self.user_01.role_line_ids[0].id, False)],
        })
        history_lines_4 = self.history_line_model.search([
            ('user_id', '=', self.user_01.id),
            ('id', 'not in', (history_lines_1 | history_lines_2).ids)
        ])
        self.assertTrue(history_lines_4)
        self.assertEqual(len(history_lines_4), 1)
        self.assertEqual(history_lines_4.performed_action, 'unlink')
        self.assertEqual(history_lines_4.old_role_id, self.role_01)
        self.assertFalse(history_lines_4.new_role_id)
        self.assertEqual(history_lines_4.old_date_from,
                         fields.Date.to_string(date.today()))
        self.assertFalse(history_lines_4.new_date_from)
        self.assertEqual(history_lines_4.old_date_to,
                         fields.Date.to_string(
                             date.today() + timedelta(days=5)))
        self.assertFalse(history_lines_4.new_date_to)

    def test_create_role_lines_on_new_user(self):
        """
        Data : /
        Test case :
            - create a user with a role
        Expected results :
            - new role history line created with performed_action == 'add'
        """
        new_user = self.user_model.create({
            'login': 'new_user',
            'name': 'new_user',
            'role_line_ids': [
                (0, 0, {
                    'role_id': self.role_01.id,
                })
            ]
        })
        history_lines = self.history_line_model.search([
            ('user_id', '=', new_user.id)
        ])
        self.assertTrue(history_lines)
        self.assertEqual(len(history_lines), 1)
        self.assertEqual(history_lines.performed_action, 'add')

    def test_no_create_role_lines_on_new_user(self):
        """
        Data : /
        Test case :
            - create a user without role
        Expected results :
            - no role history line created
        """
        new_user = self.user_model.create({
            'login': 'new_user',
            'name': 'new_user',
        })
        history_lines = self.history_line_model.search([
            ('user_id', '=', new_user.id)
        ])
        self.assertFalse(history_lines)
