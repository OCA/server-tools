# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html

from odoo.exceptions import AccessError
from odoo.tests import TransactionCase


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.immutable = self.env.ref('user_immutable.group_immutable')
        self.user = self.env.ref('base.user_demo')
        self.user.write({'in_group_%s' % self.immutable.id: False})

    def test_can_add_immutable(self):
        """ It should verify that `Administrator` can add users to the
         immutable group by default
         """
        self.user.write({'in_group_%s' % self.immutable.id: True})
        self.assertTrue(self.user.has_group('user_immutable.group_immutable'))

    def test_non_immutable_cannot_add_immutable(self):
        """ It should verify that other users cannot add to the immutable
        group
        """
        with self.assertRaises(AccessError):
            self.user.sudo(self.user.id).write({
                'in_group_%s' % self.immutable.id: True
            })

    def test_immutable_can_alter_immutable(self):
        """ It should verify that immutable users can alter users in the
        immutable group
        """
        self.user.write({'in_group_%s' % self.immutable.id: True})
        exp = 'Princess Peach'
        self.user.write({'name': exp})
        self.assertEquals(self.user.name, exp)

    def test_immutable_cannot_be_unlinked(self):
        """ It should make sure non `Immutable` members cannot unlink other
        `Immutable` Members
        """
        with self.assertRaises(AccessError):
            self.env.ref('base.user_root').sudo(
                self.user.id
            ).unlink()

    def test_immutable_can_be_unlinked_by_immutable(self):
        """ It should make sure `Immutable` members can unlink other
        `Immutable` Members
        """
        user = self.user.copy()
        user.write({'in_group_%s' % self.immutable.id: True})
        self.assertTrue(user.unlink())

    def test_check_immutable(self):
        """ It should raise `AccessError` when trying called by a user
        outside the `Immutable` group on an `Immutable` user
        """
        with self.assertRaises(AccessError):
            self.env.ref('base.user_root').sudo(
                self.user.id
            )._check_immutable()
