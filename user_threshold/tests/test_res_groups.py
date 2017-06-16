# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import AccessError
from .common import Common


class TestResGroups(Common):

    def test_can_write_max_users(self):
        """
        It should restrict membership additions to Threshold Managers to
        pre-existing members of that group
        """
        u = self._create_test_user()
        u.write({
            'in_group_%s' % self.env.ref('base.group_erp_manager').id: True
        })
        g = self.env.ref('user_threshold.group_threshold_manager')
        with self.assertRaises(AccessError):
            g.sudo(u.id).write({'users': self.env.ref('base.user_demo').id})

    def test_cannot_write_max_users(self):
        """
        It should restrict membership additions to Threshold Managers to
        pre-existing members of that group
        """
        u = self._create_test_user()
        self._add_user_to_group(u)
        g = self.env.ref('user_threshold.group_threshold_manager')
        demo_user = self.env.ref('base.user_demo')
        g.sudo(u.id).write({'users': [(4, [demo_user.id])]})
        self.assertTrue(demo_user.id in g.users.ids)
