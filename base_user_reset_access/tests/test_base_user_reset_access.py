# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of base_user_reset_access,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     base_user_reset_access is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     base_user_reset_access is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with base_user_reset_access.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.tests import common


class TestResetUserAccessRight(common.TransactionCase):

    def setUp(self):
        super(TestResetUserAccessRight, self).setUp()
        self.user_obj = self.env['res.users']

    def test_reset_demo_user_access_right(self):
        # I get the demo user
        demo_user = self.env.ref('base.user_demo')
        demo_user.groups_id = [(4, self.ref('base.group_no_one'))]
        demo_user.reset_access_right()
        default_groups_ids = self.user_obj._get_group()
        # I check if access right on this user are reset
        self.assertEquals(set(demo_user.groups_id.ids),
                          set(default_groups_ids))
