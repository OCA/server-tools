# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common

@common.at_install(False)
@common.post_install(True)
class TestOnchange(common.TransactionCase):

    def setUp(self):
        super(TestOnchange, self).setUp()

    def test_playing_onchange_on_model(self):
        result = self.env['res.partner'].play_onchanges({
            'company_type': 'company',
        }, ['company_type'])
        self.assertEqual(result['is_company'], True)

    def test_playing_onchange_on_record(self):
        company = self.env.ref('base.main_company')
        result = company.play_onchanges({
            'email': 'contact@akretion.com',
            'rml_footer': u'Website: http://www.akretion.com'},
            ['email'])
        # rml_footer is not changed by play_onchanges.
        self.assertEqual(
            result['rml_footer'],
            u'Website: http://www.akretion.com')
        result = company.with_context(overwrite_values=True).play_onchanges({
            'email': 'contact@akretion.com',
            'rml_footer': u'Website: http://www.akretion.com'},
            ['email'])
        # rml_footer is overwrited by play_onchanges.
        self.assertEqual(
            result['rml_footer'],
            u'Email: contact@akretion.com | Website: '
            u'http://www.yourcompany.com')
        self.assertEqual(company.email, u'info@yourcompany.com')
