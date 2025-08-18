# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Hibou Corp.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo_test_helper import FakeModelLoader

from odoo.exceptions import UserError, ValidationError
from odoo.tests import SavepointCase


class TestBaseException(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .purchase_test import ExceptionRule, LineTest, PurchaseTest

        cls.loader.update_registry((ExceptionRule, LineTest, PurchaseTest))

        cls.partner = cls.env["res.partner"].create({"name": "Foo"})
        cls.po = cls.env["base.exception.test.purchase"].create(
            {
                "name": "Test base exception to basic purchase",
                "partner_id": cls.partner.id,
                "line_ids": [
                    (0, 0, {"name": "line test", "amount": 120.0, "qty": 1.5})
                ],
            }
        )
        cls.exception_rule = cls.env["exception.rule"].create(
            {
                "name": "No ZIP code on destination",
                "sequence": 10,
                "model": "base.exception.test.purchase",
                "code": "if not self.partner_id.zip: failed=True",
                "exception_type": "by_py_code",
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_valid(self):
        self.exception_rule.active = False
        self.po.button_confirm()
        self.assertFalse(self.po.exception_ids)

    def test_fail_by_py(self):
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertTrue(self.po.exception_ids)

    def test_fail_by_domain(self):
        self.exception_rule.write(
            {
                "domain": "[('partner_id.zip', '=', False)]",
                "exception_type": "by_domain",
            }
        )
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertTrue(self.po.exception_ids)

    def test_fail_by_method(self):
        self.exception_rule.write(
            {
                "method": "exception_method_no_zip",
                "exception_type": "by_method",
            }
        )
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertTrue(self.po.exception_ids)

    def test_ignorable_exception(self):
        # Block because of exception during validation
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        # Test that we have linked exceptions
        self.assertTrue(self.po.exception_ids)
        # Test ignore exeception make possible for the po to validate
        self.po.action_ignore_exceptions()
        self.assertTrue(self.po.ignore_exception)
        self.assertFalse(self.po.exceptions_summary)
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")

    def test_blocking_exception(self):
        self.exception_rule.is_blocking = True
        # Block because of exception during validation
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        # Test that we have linked exceptions
        self.assertTrue(self.po.exception_ids)
        self.assertTrue(self.po.exceptions_summary)
        # Test cannot ignore blocked exception
        with self.assertRaises(UserError):
            self.po.action_ignore_exceptions()
        self.assertFalse(self.po.ignore_exception)
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertTrue(self.po.exception_ids)
        self.assertTrue(self.po.exceptions_summary)

    def test_fail_by_py_batch(self):
        self.exception_rule.write(
            {
                "code": "failed = self.filtered(lambda po: not po.partner_id.zip)",
                "exception_type": "by_py_code_batch",
            }
        )
        po2 = self.po.copy()
        pos = self.po | po2

        with self.assertRaises(ValidationError):
            pos.button_confirm()

        self.assertEqual(self.po.exception_ids, self.exception_rule)
        self.assertEqual(po2.exception_ids, self.exception_rule)

        self.exception_rule.write(
            {
                "code": "raise Exception(sorted(self, key=lambda po: po.id))",
            }
        )

        with self.assertRaises(UserError) as e:
            pos.detect_exceptions()

        # Ensure that the code is really called with all orders as self
        self.assertIn(str(sorted(pos, key=lambda po: po.id)), str(e.exception))
