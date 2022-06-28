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
        cls.po = cls.env["base.exception.test.purchase"].create(
            {
                "name": "Test base exception to basic purchase",
                "partner_id": cls.env["res.partner"].create({"name": "Foo"}).id,
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
        cls.exception_rule_confirm_obj = cls.env["exception.rule.confirm"]
        cls.exception_rule_confirm = cls.exception_rule_confirm.create(
            {
                "related_model_id": cls.po.id,
                "exception_ids": [(4, cls.exception_rule.id)],
                "ignore": False,
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        return super().tearDownClass()

    def test_valid(self):
        self.exception_rule.active = False
        self.po.button_confirm()
        self.assertFalse(self.po.exception_ids)

    def test_exception_rule_confirm(self):
        self.exception_rule_confirm.action_confirm()
        self.assertFalse(self.exception_rule_confirm.exception_ids)

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

    def test_purchase_check_exception(self):
        self.po.test_purchase_check_exception()

    def test_purchase_check_button_approve(self):
        self.po.button_approve()
        self.assertEqual(self.po.state, "to approve")

    def test_purchase_check_button_draft(self):
        self.po.button_draft()
        self.assertEqual(self.po.state, "draft")

    def test_purchase_check_button_confirm(self):
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")

    def test_purchase_check_button_cancel(self):
        self.po.button_cancel()
        self.assertEqual(self.po.state, "cancel")

    def test_detect_exceptions(self):
        self.po.detect_exceptions()

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
