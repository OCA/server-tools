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

    def test_exception_in_sub_records(self):
        self.exception_rule.active = False
        line = self.po.line_ids[0]
        line.amount = 90

        self.po.detect_exceptions()

        self.assertEqual(self.po.exception_ids, self.sub_exception_rule)
        # Even if the exception was not raised by self.po, its description must still
        # be in the summary of it
        self.assertIn(self.sub_exception_rule.description, self.po.exceptions_summary)

        self.assertEqual(line.main_exception_id, self.sub_exception_rule)
        self.assertEqual(line.exception_ids, self.sub_exception_rule)
        self.assertIn(
            self.sub_exception_rule.description,
            line.exceptions_summary,
        )
        # self.po has 2 lines, the exception is detected only on the 1st line.
        # The 2nd line must not have any exception assigned or summary set
        self.assertFalse(self.po.line_ids[1].exception_ids)
        self.assertFalse(self.po.line_ids[1].exceptions_summary)

        self.exception_rule.active = True

        self.po.detect_exceptions()

        # Now both exceptions must be assigned to the record, in the right order
        self.assertEqual(self.po.exception_ids[0], self.sub_exception_rule)
        self.assertEqual(self.po.exception_ids[1], self.exception_rule)

        self.po.line_ids[1].amount = 80
        self.po.detect_exceptions()

        self.assertEqual(line.exception_ids, self.sub_exception_rule)
        self.assertEqual(self.po.line_ids[1].exception_ids, self.sub_exception_rule)
        self.assertIn(
            self.sub_exception_rule.description,
            self.po.line_ids[1].exceptions_summary,
        )

        line.amount = 200
        line.detect_exceptions()

        # Updating sub-exceptions must update exceptions on parent
        self.assertFalse(line.exception_ids)
        self.assertEqual(self.po.exception_ids, self.exception_rule)

    def test_exception_in_sub_record_method(self):
        self.exception_rule.active = False

        self.po.line_method_ids.amount = 90
        # Model has no exception_ids and returns self.lead_id in _get_main_records,
        # that's why the exceptions are added to the parent
        self.po.line_method_ids.detect_exceptions()

        self.assertEqual(self.po.exception_ids, self.sub_exception_rule_method)
        self.assertIn(
            self.sub_exception_rule_method.description,
            self.po.exceptions_summary,
        )

        self.po.line_method_ids.amount = 200
        self.po.detect_exceptions()
        # Parent implemented line_method_ids in _get_sub_exception_field_names,
        # that's why the exceptions were detected on child records but none was found
        self.assertFalse(self.po.exception_ids)
