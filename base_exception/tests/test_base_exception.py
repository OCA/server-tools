# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Hibou Corp.
# Copyright 2025 Raumschmiede GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.exceptions import UserError, ValidationError

from .common import TestBaseExceptionCommon


class TestBaseException(TestBaseExceptionCommon):
    def test_valid(self):
        self.exception_rule.active = False
        self.po.button_confirm()
        self.assertFalse(self.po.exception_ids)

    def test_fail_by_py(self):
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertEqual(self.po.exception_ids, self.exception_rule)

    def test_fail_by_domain(self):
        self.exception_rule.write(
            {
                "domain": "[('partner_id.zip', '=', False)]",
                "exception_type": "by_domain",
            }
        )
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertEqual(self.po.exception_ids, self.exception_rule)
        self.assertIn(self.exception_rule.description, self.po.exceptions_summary)

    def test_fail_by_method(self):
        self.exception_rule.write(
            {
                "method": "exception_method_no_zip",
                "exception_type": "by_method",
            }
        )
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertEqual(self.po.exception_ids, self.exception_rule)

    def test_ignorable_exception(self):
        # Block because of exception during validation
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        # Test that we have linked exceptions
        self.assertEqual(self.po.exception_ids, self.exception_rule)
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
        self.assertEqual(self.po.exception_ids, self.exception_rule)
        self.assertTrue(self.po.exceptions_summary)
        # Test cannot ignore blocked exception
        with self.assertRaises(UserError):
            self.po.action_ignore_exceptions()
        self.assertFalse(self.po.ignore_exception)
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.assertEqual(self.po.exception_ids, self.exception_rule)
        self.assertTrue(self.po.exceptions_summary)
