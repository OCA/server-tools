# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestResetUserAccessRight(common.TransactionCase):

    def setUp(self):
        super(TestResetUserAccessRight, self).setUp()
        self.user_obj = self.env['res.users']

    def test_reset_demo_user_access_right(self):
        # I get the demo user
        demo_user = self.env.ref('base.user_demo')
        demo_user.groups_id = [(4, self.ref('base.group_no_one'))]
        demo_user.reset_access_right()
        default_groups_ids = self.user_obj._default_groups()
        # I check if access right on this user are reset
        self.assertEquals(set(demo_user.groups_id),
                          set(default_groups_ids))
