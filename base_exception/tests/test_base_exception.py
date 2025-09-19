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

        desc = "Line {{line}} must have price greater than 100"
        self.sub_exception_rule.description = desc
        # Jinja content was not parsed, must still contain the syntax
        self.assertIn(
            "{{line}}",
            self.po.exceptions_summary,
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

    def test_description_jinja_success(self):
        self.maxDiff = None
        self.exception_rule.description_text_type = "jinja"
        desc = "{{object.partner_id.name}} has no ZIP. Model: {{exception.model}}"
        self.exception_rule.description = desc
        self.exception_rule.is_blocking = True

        self.po.detect_exceptions()

        self.assertIn(self.po.partner_id.name, self.po.exceptions_summary)
        self.assertIn(self.po._name, self.po.exceptions_summary)

        self.sub_exception_rule.description_text_type = "jinja"
        self.sub_exception_rule.description = (
            "Line's price {{object.amount}} is lower than 100"
        )
        line = self.po.line_ids[0]
        line.amount = 90
        self.po.detect_exceptions()

        self.assertIn(str(line.amount), self.po.exceptions_summary)
        self.assertIn(str(line.amount), line.exceptions_summary)

        line2 = self.po.line_ids[1]
        line2.amount = 80
        self.po.detect_exceptions()
        self.po.invalidate_cache()

        # Both lines have the same exception but each line has a unique description.
        # Summary of parent must have both descriptions
        self.assertIn(str(line2.amount), line2.exceptions_summary)
        self.assertNotIn(str(line.amount), line2.exceptions_summary)
        self.assertEqual(
            self.po.exceptions_summary,
            "<ul>"
            "<li>Amount less than 100: <i>Line's price 90.0 is lower than 100</i></li>"
            "<li>Amount less than 100: <i>Line's price 80.0 is lower than 100</i></li>"
            "<li>No ZIP code on destination: "
            "<i>Foo has no ZIP. Model: base.exception.test.purchase</i> "
            "<b>(Blocking exception)</b>"
            "</li>"
            "</ul>",
        )

        # Use a field here that only exist on base.exception.test.purchase and not on
        # base.exception.method.test.purchase.line to assert that the passed record is
        # self and not a method line
        desc = "PO in state {{obj.state}} has invalid data"
        self.sub_exception_rule_method.description = desc
        self.sub_exception_rule_method.description_text_type = "jinja"

        method_line = self.po.line_method_ids[0]
        method_line.amount = 70
        self.po.detect_exceptions()
        self.po.invalidate_cache()

        self.assertIn(self.sub_exception_rule_method, self.po.exception_ids)
        self.assertIn(
            "PO in state draft has invalid data",
            self.po.exceptions_summary,
        )

    def test_description_jinja_error(self):
        self.exception_rule.description = "Partner ${name.field} has no ZIP"
        self.exception_rule.description_text_type = "jinja"

        self.po.detect_exceptions()
        # Computation does not raise an error but because Jinja syntax is wrong
        # the syntax must still be in the summary
        self.po._compute_exceptions_summary()
        self.assertIn("name.field", self.po.exceptions_summary)

        self.exception_rule.description = "Partner {{name.field}} has no ZIP"
        self.po.detect_exceptions()
        # Computation of exceptions_summary raises an error.
        # Here because "name" is not available in the Jinja context
        with self.assertRaises(UserError) as e:
            self.po._compute_exceptions_summary()
        self.assertIn("is undefined", str(e.exception))

        desc = "Partner {{object.filtered(lambda o: o.name)}} has no ZIP"
        self.exception_rule.description = desc

        self.po.detect_exceptions()
        # Jinja doesn't like lambda
        with self.assertRaises(UserError) as e:
            self.po._compute_exceptions_summary()
        self.assertIn("expected token", str(e.exception))

        desc = "Partner {{object.unexisting_field}} has no ZIP"
        self.exception_rule.description = desc

        # Using an non-existing field works but nothing is rendered
        self.po.detect_exceptions()
        self.assertIn("Partner  has no ZIP", self.po.exceptions_summary)

        desc = "Partner {{object.fi.fu}} has no ZIP"
        self.exception_rule.description = desc

        self.po.detect_exceptions()
        # But Jinja raises an error when a sub-field is used of a non-existing field
        with self.assertRaises(UserError) as e:
            self.po._compute_exceptions_summary()
        self.assertIn("has no attribute 'fi'", str(e.exception))

        self.exception_rule.active = False

        # User expected that base.exception.method.test.purchase.line can be used as
        # record in the description because the model on the exception is set to this.
        # But models inheriting from base.exception.method can't be used. Must not work
        desc = "Method Line of {{object.lead_id.name}} has invalid data"
        self.sub_exception_rule_method.description = desc
        self.sub_exception_rule_method.description_text_type = "jinja"

        method_line = self.po.line_method_ids[0]
        method_line.amount = 70
        self.po.detect_exceptions()
        with self.assertRaises(UserError) as e:
            self.po._compute_exceptions_summary()

        self.assertIn(
            "odoo.api.base.exception.test.purchase object' has no attribute 'lead_id'",
            str(e.exception),
        )
