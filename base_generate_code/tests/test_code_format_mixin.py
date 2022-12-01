# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from string import ascii_lowercase, ascii_uppercase, digits

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import SavepointCase


class TestCodeFormatMixin(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .fake_models import FakeProduct, FakeProductFactory

        cls.loader.update_registry((FakeProductFactory, FakeProduct))

        factory = cls.env["fake.product.factory"]

        cls.factory_1 = factory.create({"code_mask": "XXX-000"})

        cls.factory_2 = factory.create({"code_mask": "Xxx-000-x0X0"})

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def _reverse_mask(self, code):
        reverse_mask = ""
        for car in code:
            if car in ascii_uppercase:
                reverse_mask += "X"
            elif car in ascii_lowercase:
                reverse_mask += "x"
            elif car in digits:
                reverse_mask += "0"
            else:
                reverse_mask += car
        return reverse_mask

    def test_1_default_code_format(self):
        self.factory_1.code_mask = ""

        product = self.env["fake.product"]
        product_1 = product.create({"tmpl_id": self.factory_1.id})
        self._reverse_mask(product_1.code)
        self.assertEqual(self._reverse_mask(product_1.code), "XXXXXX-00")

    def test_2_custom_code(self):

        product = self.env["fake.product"]
        product_1 = product.create({"tmpl_id": self.factory_1.id})
        self._reverse_mask(product_1.code)
        self.assertEqual(self._reverse_mask(product_1.code), self.factory_1.code_mask)

        product_2 = product.create({"tmpl_id": self.factory_2.id})
        self.assertEqual(self._reverse_mask(product_2.code), self.factory_2.code_mask)
