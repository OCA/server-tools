# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (http://www.onestein.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import common


class TestImportSecurityGroup(common.TransactionCase):
    def setUp(self):
        super(TestImportSecurityGroup, self).setUp()
        self.Access = self.env['ir.model.access']
        self.user_test = self.env.ref('base.user_demo')

    def test_01_load(self):

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

        res = self.Access.load(fields, data)

        self.assertEqual(res['ids'], False)
        self.assertEqual(len(res['messages']), 2)
        self.assertEqual(
            res['messages'][0]['message'],
            "Missing required value for the field 'Object' (model_id)")
        self.assertEqual(
            res['messages'][1]['message'],
            "Missing required value for the field 'Object' (model_id)")

        res2 = self.Access.sudo(self.user_test).load(fields, data)

        self.assertEqual(res2['ids'], None)
        self.assertEqual(len(res2['messages']), 1)
        self.assertEqual(
            res2['messages'][0]['message'],
            'User (ID: %s) is not allowed to import data in '
            'model ir.model.access.' % self.user_test.id)
