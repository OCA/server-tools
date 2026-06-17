# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Hibou Corp.
# Copyright 2025 Raumschmiede GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo_test_helper import FakeModelLoader

from odoo.tests import SavepointCase


class TestBaseExceptionCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .purchase_test import ExceptionRule, LineTest, LineTestMethod, PurchaseTest

        cls.loader.update_registry(
            (ExceptionRule, LineTest, LineTestMethod, PurchaseTest)
        )

        cls.partner = cls.env["res.partner"].create({"name": "Foo"})
        cls.po = cls.env["base.exception.test.purchase"].create(
            {
                "name": "Test base exception to basic purchase",
                "partner_id": cls.partner.id,
                "line_ids": [
                    (0, 0, {"name": "line test", "amount": 120.0, "qty": 1.5}),
                    (0, 0, {"name": "line test 2", "amount": 220.0, "qty": 1.5}),
                ],
                "line_method_ids": [
                    (0, 0, {"name": "line test", "amount": 120.0, "qty": 1.5}),
                    (0, 0, {"name": "line test 2", "amount": 220.0, "qty": 1.5}),
                ],
            }
        )
        cls.exception_rule = cls.env["exception.rule"].create(
            {
                "name": "No ZIP code on destination",
                "description": "Plz set ZIP code on destination",
                "sequence": 10,
                "model": "base.exception.test.purchase",
                "code": "if not self.partner_id.zip: failed=True",
                "exception_type": "by_py_code",
            }
        )
        cls.sub_exception_rule = cls.env["exception.rule"].create(
            {
                "name": "Amount less than 100",
                "description": "Line must have price greater than 100",
                "sequence": 9,
                "model": "base.exception.test.purchase.line",
                "code": "failed = self.amount < 100",
                "exception_type": "by_py_code",
            }
        )
        cls.sub_exception_rule_method = cls.env["exception.rule"].create(
            {
                "name": "Amount less than 100",
                "description": "Method Line must have price greater than 100",
                "sequence": 9,
                "model": "base.exception.method.test.purchase.line",
                "code": "failed = self.amount < 100",
                "exception_type": "by_py_code",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()
