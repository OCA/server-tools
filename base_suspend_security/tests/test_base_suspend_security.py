# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import exceptions
from odoo.tests.common import TransactionCase
from ..base_suspend_security import BaseSuspendSecurityUid


class TestBaseSuspendSecurity(TransactionCase):
    def test_base_suspend_security(self):
        user_id = self.env.ref('base.user_demo').id
        other_company = self.env['res.company'].create({
            'name': 'other company',
            # without this, a partner is created and mail's constraint on
            # notify_email kicks in
            'partner_id': self.env.ref('base.partner_demo').id,
        })
        # be sure what we try is forbidden
        with self.assertRaises(exceptions.AccessError):
            self.env.ref('base.user_root').sudo(user_id).name = 'test'
        with self.assertRaises(exceptions.AccessError):
            other_company.sudo(user_id).name = 'test'
        # this tests ir.model.access
        self.env.ref('base.user_root').sudo(user_id).suspend_security().write({
            'name': 'test'})
        self.assertEqual(self.env.ref('base.user_root').name, 'test')
        self.assertEqual(self.env.ref('base.user_root').write_uid.id, user_id)
        # this tests ir.rule
        other_company.sudo(user_id).suspend_security().write({'name': 'test'})
        self.assertEqual(other_company.name, 'test')
        self.assertEqual(other_company.write_uid.id, user_id)
        # this tests if _normalize_args conversion works
        self.env['res.users'].browse(
            self.env['res.users'].suspend_security().env.uid)

    def test_base_suspend_security_uid(self):
        """ Test corner cases of dunder functions """
        uid = BaseSuspendSecurityUid(42)
        self.assertFalse(uid == 42)
        self.assertEqual(uid[0], 42)
        self.assertFalse(uid[1:])
        with self.assertRaises(IndexError):
            self.env['res.users'].browse(uid[1])

    def test_suspend_security_on_search(self):
        user_without_access = self.env["res.users"].create(
            dict(
                name="Testing Suspend Security",
                login="nogroups",
                email="nogroups@suspendsecurity.com",
                groups_id=[(5,)],
            )
        )
        model = self.env["ir.config_parameter"]
        # the search is forbidden
        with self.assertRaises(exceptions.AccessError):
            model.sudo(user_without_access).search([])
        # this tests the search
            model.sudo(user_without_access).suspend_security().search([])
        # be sure we can search suspended uids like ints
        partners = self.env['res.partner'].with_context(
            active_test=False,
        ).search([
            ('user_ids', '=', user_without_access.suspend_security().env.uid),
        ])
        self.assertTrue(partners)
