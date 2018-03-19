# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase


class TestQuickCreate(TransactionCase):

    def setUp(self, *args, **kwargs):
        super(TestQuickCreate, self).setUp()
        model_model = self.env['ir.model']
        self.partner_model = model_model.search([
            ('model', '=', 'res.partner')])

    def test_quick_create(self):
        partner_id = self.env['res.partner'].name_create('TEST partner')
        self.assertEqual(bool(partner_id), True)

        # Setting the flag, patches the method
        self.partner_model.avoid_quick_create = True
        with self.assertRaises(UserError):
            self.env['res.partner'].name_create('TEST partner')

        # Unsetting the flag, unpatches the method
        self.partner_model.avoid_quick_create = False
        partner_id = self.env['res.partner'].name_create('TEST partner')
        self.assertEqual(bool(partner_id), True)
