# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import TransactionCase


class TestSearchMultiValue(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .test_models import ResPartner

        cls.loader.update_registry((ResPartner,))

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.loader.restore_registry()
        return super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.partners = self.env["res.partner"]
        for i in range(1, 10):
            self.partners += self.env["res.partner"].create(
                {"name": f"Testpartner{i}", "email": f"email@test{i}"}
            )
        self.names = self.partners.mapped("name")
        self.emails = self.partners.mapped("email")

    def test_multi_search(self):
        self.assertEqual(
            self.partners,
            self.env["res.partner"].search(
                [("search_multi", "=", " ".join(self.names))]
            ),
        )
        self.assertEqual(
            self.partners,
            self.env["res.partner"].search(
                [("search_multi", "=", " ".join(self.emails))]
            ),
        )
