# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from lxml import etree

from odoo.exceptions import AccessError
from .common import Common


class TestResCompany(Common):

    def test_fields_view_get(self):
        """ It should verify that setting HIDE_THRESHOLD removes the parameter
        from the view
        """
        import odoo.addons.user_threshold.models.res_company as mdl
        mdl.HIDE_THRESHOLD = True
        view = self.env.ref('user_threshold.view_company_form')
        c = self.env['res.company'].browse(1)
        ret = c.fields_view_get(view.id)
        doc = etree.XML(ret['arch'])
        self.assertEquals(doc.xpath("//field[@name='max_users']"), [])

    def test_can_write_max_users(self):
        """ It should restrict the max users parameter to Threshold Managers
        """
        u = self._create_test_user()
        self._add_user_to_group(u)
        c = self.env['res.company'].browse(1)
        res = 10
        c.sudo(u.id).write({'max_users': res})
        self.assertEquals(c.max_users, res)

    def test_cannot_write_max_users(self):
        """ It should restrict the max users parameter to Threshold Managers
        """
        u = self._create_test_user()
        c = self.env['res.company'].browse(1)
        with self.assertRaises(AccessError):
            c.sudo(u.id).write({'max_users': 10})
