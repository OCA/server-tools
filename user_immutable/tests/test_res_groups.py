# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase


class TestResGroups(TransactionCase):

    def setUp(self):
        super(TestResGroups, self).setUp()
        self.immutable = self.env.ref('user_immutable.group_immutable')
        self.user = self.env.ref('base.user_demo')
        self.user.write({'in_group_%s' % self.immutable.id: False})

    def test_can_add_immutable(self):
        """ It should make sure that `Administrator` can add users to the
         immutable group by default """
        self.immutable.write({'users': [(4, [self.user.id])]})
        self.assertTrue(self.user.has_group('user_immutable.group_immutable'))

    def test_non_immutable_cannot_add_immutable(self):
        """ It should make sure that other users cannot add to the immutable
        group """
        immutable = self.env.ref('user_immutable.group_immutable')
        with self.assertRaises(AccessError):
            immutable.sudo(self.user.id).write({'users': [self.user.id]})
