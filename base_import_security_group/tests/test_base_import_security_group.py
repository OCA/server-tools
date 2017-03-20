# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (http://www.onestein.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import common


class TestImportSecurityGroup(common.HttpCase):
    def setUp(self):
        super(TestImportSecurityGroup, self).setUp()
        self.Access = self.env['ir.model.access']
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
            link, code, "$('button.o_list_button_add').length",
            login=user.login)

    def test_01_load(self):
        """ Admin user can import data, but the demo user cannot """
        fields = (
            'id',
            'name',
            'perm_read',
            'perm_write',
            'perm_create',
            'perm_unlink',
        )

        data = [
            ('access_res_users_test', 'res.users test', '1', '0', '0', '0',),
            ('access_res_users_test2', 'res.users test2', '1', '1', '1', '1'),
        ]

        self.has_button_import(user=self.env.user)
        res = self.Access.load(fields, data)

        self.assertEqual(res['ids'], False)
        self.assertEqual(len(res['messages']), 2)
        self.assertEqual(
            res['messages'][0]['message'],
            "Missing required value for the field 'Object' (model_id)")
        self.assertEqual(
            res['messages'][1]['message'],
            "Missing required value for the field 'Object' (model_id)")

        self.has_button_import(falsify=True, user=self.user_test)
        res2 = self.Access.sudo(self.user_test).load(fields, data)

        self.assertEqual(res2['ids'], None)
        self.assertEqual(len(res2['messages']), 1)
        self.assertEqual(
            res2['messages'][0]['message'],
            'User (ID: %s) is not allowed to import data in '
            'model ir.model.access.' % self.user_test.id)
