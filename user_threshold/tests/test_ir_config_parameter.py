# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo.exceptions import AccessError
from .common import Common, MAX_DB_USER_PARAM


class TestIrConfigParameter(Common):

    def _get_param(self):
        return self.env['ir.config_parameter'].search([
            ('key', '=', MAX_DB_USER_PARAM),
        ])

    def test_can_set(self):
        """
        It should test that users in the Threshold Manager group can
        update the parameter
        """
        mdl = self.env['ir.config_parameter']
        u = self._create_test_user()
        self._add_user_to_group(u)
        exp = '20'
        mdl.sudo(u.id).set_param(MAX_DB_USER_PARAM, exp)
        self.assertEquals(mdl.get_param(MAX_DB_USER_PARAM), exp)

    def test_cannot_set(self):
        """
        It should test that users NOT in the Threshold Manager group
        cannot alter the parameter
        """
        u = self._create_test_user()
        with self.assertRaises(AccessError):
            self.env['ir.config_parameter'].sudo(u.id).set_param(
                MAX_DB_USER_PARAM, 20
            )

    def test_can_unlink(self):
        """
        It should test that users in the Threshold Manager group can
        unlink the Threshold Param
        """
        u = self._create_test_user()
        self._add_user_to_group(u)
        param = self._get_param()
        self.assertTrue(param.sudo(u.id).unlink())

    def test_cannot_unlink(self):
        """
        It should test that users outside the Threshold Manager group
        cannot unlink the Threshold Param
        """
        u = self._create_test_user()
        param = self._get_param()
        system_group = self.env.ref('base.group_system')
        u.write({'in_group_%s' % system_group.id: True})
        with self.assertRaises(AccessError):
            param.sudo(u.id).unlink()

    def test_can_write(self):
        """
        It should test that users in the Threshold Manager group can
        write the Threshold Param
        """
        u = self._create_test_user()
        self._add_user_to_group(u)
        param = self._get_param()
        res = '10'
        param.sudo(u.id).write({'value': res})
        self.assertEquals(param.value, res)

    def test_cannot_write(self):
        """
        It should test that users outside the Threshold Manager group
        cannot write the Threshold Param
        """
        u = self._create_test_user()
        system_group = self.env.ref('base.group_system')
        access_group = self.env.ref('base.group_erp_manager')
        u.write({
            'in_group_%s' % system_group.id: True,
            'in_group_%s' % access_group.id: True,
        })
        param = self._get_param()
        with self.assertRaises(AccessError):
            param.sudo(u.id).write({'value': '10'})
