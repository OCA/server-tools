# Copyright 2017 LasLabs Inc.
# Copyright 2019 Rubén Bravo <rubenred18@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestResLang(TransactionCase):

    def setUp(self):
        super(TestResLang, self).setUp()
        self.lang = self.env.ref('base.lang_en')
        self.env.user.lang = self.lang.code
        self.uom = self.env.ref('uom.product_uom_dozen')
        self.lang.default_uom_ids = [(6, 0, self.uom.ids)]

    def test_check_default_uom_ids_fail(self):
        """It should not allow multiple UoMs of the same category."""
        with self.assertRaises(ValidationError):
            self.lang.default_uom_ids = [
                (4, self.env.ref('uom.product_uom_unit').id),
            ]

    def test_check_default_uom_ids_pass(self):
        """It should allow multiple UoMs of different categories."""
        self.lang.default_uom_ids = [
            (4, self.env.ref('uom.product_uom_kgm').id),
        ]
        self.assertEqual(len(self.lang.default_uom_ids), 2)

    def test_default_uom_by_category_exist(self):
        """It should return the default UoM if existing."""
        self.assertEqual(
            self.env['res.lang'].default_uom_by_category('Unit'),
            self.uom,
        )

    def test_default_uom_by_category_no_exist(self):
        """It should return empty recordset when no default UoM."""
        self.assertEqual(
            self.env['res.lang'].default_uom_by_category('Volume'),
            self.env['uom.uom'].browse(),
        )
