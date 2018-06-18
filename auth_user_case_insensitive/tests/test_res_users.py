# -*- coding: utf-8 -*-
# Copyright 2015-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, registry
from odoo.tests.common import TransactionCase


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.login = 'LasLabs@ExAmPlE.CoM'
        self.partner_vals = {
            'name': 'Partner',
            'is_company': False,
            'email': self.login,
        }
        self.vals = {
            'name': 'User',
            'login': self.login,
            'password': 'password',
        }
        self.model_obj = self.env['res.users']

    def _new_record(self):
        """ It should enerate a new record to test with """
        partner_id = self.env['res.partner'].create(self.partner_vals)
        self.vals['partner_id'] = partner_id.id
        return self.model_obj.create(self.vals)

    def test_login_is_lowercased_on_create(self):
        """ It should verify the login is set to lowercase on create """
        rec_id = self._new_record()
        self.assertEqual(
            self.login.lower(), rec_id.login,
            'Login was not lowercased when saved to db.',
        )

    def test_login_is_lowercased_on_write(self):
        """ It should verify the login is set to lowercase on write """
        rec_id = self._new_record()
        rec_id.write({'login': self.login})
        self.assertEqual(
            self.login.lower(), rec_id.login,
            'Login was not lowercased when saved to db.',
        )

    def test_login_login_is_lowercased(self):
        """ It should verify the login is set to lowercase on login """
        rec_id = self._new_record()
        # We have to commit this cursor, because `_login` uses a fresh cursor
        self.env.cr.commit()
        res_id = self.model_obj._login(
            self.env.registry.db_name, self.login.upper(), 'password'
        )
        # Now clean up our mess to preserve idempotence
        with api.Environment.manage():
            with registry(self.env.registry.db_name).cursor() as new_cr:
                new_cr.execute(
                    "DELETE FROM res_users WHERE login='%s'" %
                    self.login.lower()
                )
                new_cr.commit()
        self.assertEqual(
            rec_id.id, res_id,
            'Login with with uppercase chars was not successful',
        )
