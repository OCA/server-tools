# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase


class TestBaseIrFiltersDisable(TransactionCase):
    def test_base_ir_filters_disable(self):
        new_filter = self.env['ir.filters'].create({
            'name': 'inactive testfilter',
            'user_id': False,
            'domain': '[]',
            'context': '{}',
            'model_id': 'ir.filters',
            'active': False,
        })
        self.assertFalse(self.env['ir.filters'].search([]) & new_filter)
        self.assertTrue(
            self.env['ir.filters'].with_context(active_test=False).search([]) &
            new_filter)
