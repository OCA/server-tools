# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

import time

from openerp.tests.common import TransactionCase

from ..exceptions import PassError


class TestResUsers(TransactionCase):

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.main_comp = self.env.ref('base.main_company')
        # Modify users as privileged, but non-root user
        privileged_user = self.env['res.users'].create({
            'name': 'Privileged User',
            'login': 'privileged_user@example.com',
            'company_id': self.main_comp.id,
            'groups_id': [(4, self.env.ref('base.group_erp_manager').id)],
        })
        privileged_user.email = privileged_user.login
        self.env = self.env(user=privileged_user)
        self.login = 'foslabs@example.com'
        self.partner_vals = {
            'name': 'Partner',
            'is_company': False,
            'email': self.login,
        }
        self.password = 'asdQWE123$%^'
        self.vals = {
            'name': 'User',
            'login': self.login,
            'password': self.password,
            'company_id': self.main_comp.id
        }
        self.model_obj = self.env['res.users']

    def _new_record(self):
        partner_id = self.env['res.partner'].create(self.partner_vals)
        self.vals['partner_id'] = partner_id.id
        return self.model_obj.create(self.vals)

    def test_password_write_date_is_saved_on_create(self):
        rec_id = self._new_record()
        self.assertTrue(
            rec_id.password_write_date,
            'Password write date was not saved to db.',
        )

    def test_password_write_date_is_updated_on_write(self):
        rec_id = self._new_record()
        old_write_date = rec_id.password_write_date
        time.sleep(2)
        rec_id.write({'password': 'asdQWE123$%^2'})
        rec_id.refresh()
        new_write_date = rec_id.password_write_date
        self.assertNotEqual(
            old_write_date, new_write_date,
            'Password write date was not updated on write.',
        )

    def test_does_not_update_write_date_if_password_unchanged(self):
        rec_id = self._new_record()
        old_write_date = rec_id.password_write_date
        time.sleep(2)
        rec_id.write({'name': 'Luser'})
        rec_id.refresh()
        new_write_date = rec_id.password_write_date
        self.assertEqual(
            old_write_date, new_write_date,
            'Password not changed but write date updated anyway.',
        )

    def test_check_password_returns_true_for_valid_password(self):
        rec_id = self._new_record()
        self.assertTrue(
            rec_id.check_password('asdQWE123$%^3'),
            'Password is valid but check failed.',
        )

    def test_check_password_raises_error_for_invalid_password(self):
        rec_id = self._new_record()
        with self.assertRaises(PassError):
            rec_id.check_password('password')

    def test_save_password_crypt(self):
        rec_id = self._new_record()
        self.assertEqual(
            1, len(rec_id.password_history_ids),
        )

    def test_check_password_crypt(self):
        """ It should raise PassError if previously used """
        rec_id = self._new_record()
        with self.assertRaises(PassError):
            rec_id.write({'password': self.password})

    def test_password_is_expired_if_record_has_no_write_date(self):
        rec_id = self._new_record()
        rec_id.write({'password_write_date': None})
        rec_id.refresh()
        self.assertTrue(
            rec_id._password_has_expired(),
            'Record has no password write date but check failed.',
        )

    def test_an_old_password_is_expired(self):
        rec_id = self._new_record()
        old_write_date = '1970-01-01 00:00:00'
        rec_id.write({'password_write_date': old_write_date})
        rec_id.refresh()
        self.assertTrue(
            rec_id._password_has_expired(),
            'Password is out of date but check failed.',
        )

    def test_a_new_password_is_not_expired(self):
        rec_id = self._new_record()
        self.assertFalse(
            rec_id._password_has_expired(),
            'Password was just created but has already expired.',
        )

    def test_expire_password_generates_token(self):
        rec_id = self._new_record()
        rec_id.sudo().action_expire_password()
        rec_id.refresh()
        token = rec_id.partner_id.signup_token
        self.assertTrue(
            token,
            'A token was not generated.',
        )

    def test_validate_pass_reset_error(self):
        """ It should throw PassError on reset inside min threshold """
        rec_id = self._new_record()
        with self.assertRaises(PassError):
            rec_id._validate_pass_reset()

    def test_validate_pass_reset_allow(self):
        """ It should allow reset pass when outside threshold """
        rec_id = self._new_record()
        rec_id.password_write_date = '2016-01-01'
        self.assertEqual(
            True, rec_id._validate_pass_reset(),
        )

    def test_validate_pass_reset_zero(self):
        """ It should allow reset pass when <= 0 """
        rec_id = self._new_record()
        rec_id.company_id.password_minimum = 0
        self.assertEqual(
            True, rec_id._validate_pass_reset(),
        )
