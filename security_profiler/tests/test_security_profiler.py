# Copyright 2019 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from ..models.ir_model import _check_action_profiled_user


class TestSecurityProfiler(TransactionCase):

    def setUp(self):
        super(TestSecurityProfiler, self).setUp()
        self.user_model = self.env['res.users']
        self.partner_model = self.env['res.partner']
        self.group_model = self.env['res.groups']
        self.menu_model = self.env['ir.ui.menu']
        self.action_model = self.env['ir.actions.act_window']
        self.report_model = self.env[
            'report.security_profiler.res_users_profiler_sessions_report']

        self.employee_group = self.env.ref('base.group_user')
        self.category_hidden = self.env.ref('base.module_category_hidden')

        self.action_contacts = self.action_model.create({
            'name': 'contacts',
            'res_model': 'res.partner',
        })

        self.user = self.user_model.create({
            'name': "USER TEST",
            'login': 'user_test',
            'groups_id': [(6, 0, [self.employee_group.id])],
        })

        self.group = self.group_model.create({
            'name': "GROUP TEST",
            'implied_ids': [(6, 0, [self.employee_group.id])],
            'category_id': self.category_hidden.id,
        })

        self.user.groups_id += self.group

        self.menu_parent = self.menu_model.create({
            'name': "Parent Menu",
            'groups_id': [(6, 0, [self.group.id])],
        })
        self.menu_child = self.menu_model.create({
            'name': "Child Menu",
            'parent_id': self.menu_parent.id,
            'action': 'ir.actions.act_window,%s' % self.action_contacts.id,
        })
        self.menus = self.menu_parent + self.menu_child

        self.session = self.env['res.users.profiler.sessions'].create({
            'user_id': self.user.id,
            'active': True,
            'user_role_name': 'Contact Reader Test',
            'implied_groups': [(6, 0, [self.employee_group.id])],
        })

    def test_1(self):
        session_2 = self.env['res.users.profiler.sessions'].create({
            'user_id': self.user.id,
            'user_role_name': 'Second Session Test',
        })
        with self.assertRaises(ValidationError):
            session_2.active = True

    def test_2(self):
        self.partner_model.sudo(self.user.id).search([])
        self.assertTrue(len(self.session.profiled_accesses_ids) > 0)
        for profiled_access in self.session.profiled_accesses_ids:
            self.assertEquals(profiled_access.res_model, 'res.partner')

        action_dict = {
            'id': self.action_contacts.id,
            'res_model': self.action_contacts.res_model,
        }
        _check_action_profiled_user(
            self.env, self.user.id, self.action_contacts.xml_id,
            action_dict, self.action_contacts.type)
        self.assertEquals(len(self.session.profiled_actions_ids), 1)
        self.assertEquals(
            self.session.profiled_actions_ids.res_model, 'res.partner')
        self.assertEquals(
            self.session.profiled_actions_ids.action, self.action_contacts)

        self.assertEquals(len(self.session.profiled_menus_ids), 2)
        for menu in self.session.profiled_menus_ids:
            self.assertTrue(menu in self.menus)
            self.assertTrue(menu not in self.session.implied_menus)

        report = self.report_model.new({})
        report_dict = report.get_report_values([self.session.id])
        report_doc = report_dict['docs'][0]
        self.assertEquals(report_doc['session'], self.session)
