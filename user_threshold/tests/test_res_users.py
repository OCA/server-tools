# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo.exceptions import AccessError, ValidationError
from .common import Common, MAX_DB_USER_PARAM


class TestResUsers(Common):

    def setUp(self):
        super(TestResUsers, self).setUp()
        self.env['ir.config_parameter'].set_param(MAX_DB_USER_PARAM, '0')

    def test_copy_global(self):
        """ It should restrict the user count in copy() as prescribed by the
        global threshold parameter
        """
        self.env['ir.config_parameter'].set_param(MAX_DB_USER_PARAM, 3)
        self._create_test_user()
        with self.assertRaises(ValidationError):
            self._create_test_user()

    def test_create_global(self):
        """ It should restrict the user count as prescribed by the global
        threshold parameter
        """
        self.env['ir.config_parameter'].set_param(MAX_DB_USER_PARAM, 3)
        self._create_test_user()
        with self.assertRaises(ValidationError):
            self.env['res.users'].create({
                'login': 'Derp Derpington',
                'email': 'dderpington@example.com',
                'notify_email': 'always',
            })

    def test_copy_company(self):
        """ It should restrict the user count in copy() as prescribed by the
        companies threshold parameter
        """
        c = self.env['res.company'].browse(1)
        c.max_users = 3
        self._create_test_user()
        with self.assertRaises(ValidationError):
            self._create_test_user()

    def test_create_company(self):
        """ It should restrict the user count as prescribed by the companies
        threshold parameter
        """
        c = self.env['res.company'].browse(1)
        c.max_users = 3
        self._create_test_user()
        with self.assertRaises(ValidationError):
            self.env['res.users'].create({
                'login': 'Derp Derpington',
                'email': 'dderpington@example.com',
                'notify_email': 'always',
            })

    def test_fields_view_get(self):
        """ It should verify that setting HIDE_THRESHOLD removes the parameter
        from the view
        """
        import odoo.addons.user_threshold.models.res_users as mdl
        mdl.HIDE_THRESHOLD = True
        view = self.env.ref('user_threshold.view_users_form')
        u = self._create_test_user()
        ret = u.fields_view_get(view.id)
        doc = etree.XML(ret['arch'])
        self.assertEquals(doc.xpath("//group[@name='user_threshold']"), [])

    def test_cannot_write_exempt(self):
        """ It should restrict the threshold exempt parameter to Threshold
        Managers
        """
        u = self._create_test_user()
        tu = self._create_test_user()
        with self.assertRaises(AccessError):
            tu.sudo(u.id).write({'threshold_exempt': True})

    def test_can_write_exempt(self):
        """ It should restrict the threshold exempt parameter to Threshold
        Managers
        """
        u = self._create_test_user()
        self._add_user_to_group(u)
        tu = self._create_test_user()
        tu.sudo(u.id).write({'threshold_exempt': True})
        self.assertEquals(tu.threshold_exempt, True)

    def test_cannot_write_group(self):
        """ It should restrict additions to the Threshold Managers to users in
        that group
        """
        u = self._create_test_user()
        u.write({
            'in_group_%s' % self.env.ref('base.group_erp_manager').id: True
        })
        tu = self._create_test_user()
        th_group = self.env.ref('user_threshold.group_threshold_manager')
        with self.assertRaises(AccessError):
            tu.sudo(u.id).write({'in_group_%s' % th_group.id: True})

    def test_can_write_group(self):
        """ It should restrict additions to the Threshold Managers to users in
        that group
        """
        u = self._create_test_user()
        self._add_user_to_group(u)
        tu = self._create_test_user()
        th_group = self.env.ref('user_threshold.group_threshold_manager')
        tu.sudo(u.id).write({'in_group_%s' % th_group.id: True})
        self.assertEquals(
            tu.has_group('user_threshold.group_threshold_manager'), True
        )
