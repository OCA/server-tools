# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase


class TestCopyUserAccess(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestCopyUserAccess, self).setUp(*args, **kwargs)

        # Objects
        self.obj_res_users = self.env['res.users']
        self.obj_wizard = self.env['base.copy_user_access']

        # Data
        self.demo_user = self.env.ref('base.user_demo')

    def _prepare_user_data(self):
        data = {
            'login': 'test_user@test.com',
            'name': 'test user',
            'password': 'a'
        }

        return data

    def test_copy_user_access(self):
        # Create New User
        data = self._prepare_user_data()
        user = self.obj_res_users.create(data)
        # Check create new user
        self.assertIsNotNone(user)

        #Fill Context
        context = self.obj_res_users.context_get()
        ctx = context.copy()
        ctx.update({'active_ids': user.ids})

        # Create Wizard
        wizard = self.obj_wizard\
            .with_context(ctx).create({'user_id': self.demo_user.id})
        wizard.with_context(ctx).copy_access_right()

        # Check group_ids(new_user) with group_ids(demo_user)
        self.assertEquals(set(self.demo_user.groups_id.ids),
                          set(user.groups_id.ids))
