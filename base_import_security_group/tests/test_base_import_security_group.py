# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (http://www.onestein.eu)
# Copyright 2021 ArcheTI (http://www.archeti.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import common


class TestImportSecurityGroup(common.HttpCase):
    def setUp(self):
        super(TestImportSecurityGroup, self).setUp()
        self.Model = self.env['res.partner.category']
        self.user_admin = self.env.ref('base.user_admin')
        self.user_test = self.env.ref('base.user_demo')

    def has_button_import(self, falsify=False, user=None):
        """
        Verify that the button is either visible or invisible.
        After the adjacent button is loaded, allow for a second for
        the asynchronous call to finish and update the visibility """
        code = """
        window.setTimeout(function () {
            if (%s$('.o_button_import').length) {
                console.log('ok');
            } else {
                console.log('error');
            };
        }, 1000);
        """ % ('!' if falsify else '')
        action = self.env.ref('base.action_partner_category_form').id
        link = '/web#action=%s' % action
        self.phantom_js(
            link, code, "$('button.o_list_button_add').length === 1",
            login=user.login)

    def test_01_load(self):
        """ Admin user can import data, but the demo user cannot """
        fields = (
            'id',
            'name',
        )

        data = [
            ('access_res_users_test', 'test'),
            ('access_res_users_test2', 'test2'),
        ]
        self.has_button_import(user=self.user_admin)
        res = self.Model.load(fields, data)

        self.assertEqual(len(res['ids']), 2)

        self.has_button_import(falsify=True, user=self.user_test)
        res2 = self.Model.sudo(self.user_test).load(fields, data)

        self.assertEqual(res2['ids'], None)
        self.assertEqual(len(res2['messages']), 1)
        self.assertEqual(
            res2['messages'][0]['message'],
            'User (ID: %s) is not allowed to import data in '
            'model res.partner.category.' % self.user_test.id)

    def test_02(self):
        """Demo user can import when added to the model import group"""
        model = self.env["ir.model"].search([
            ("model", "=", "res.partner.category")])
        model_import_group = self.env["res.groups"].create({
            "name": "foo"
        })
        model.import_group_id = model_import_group
        self.has_button_import(falsify=True, user=self.user_test)
        model_import_group.users = [(4, self.user_test.id)]
        self.has_button_import(user=self.user_test)
