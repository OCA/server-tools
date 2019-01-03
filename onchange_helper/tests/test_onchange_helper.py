# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests.common as common


class TestOnchangeHelper(common.TransactionCase):

    def test_playing_onchange_on_model(self):
        result = self.env['res.partner'].play_onchanges({
            'company_type': 'company',
        }, ['company_type'])
        self.assertEqual(result['is_company'], True)
