# -*- coding: utf-8 -*-
# Copyright 2016 Jairo Llopis <jairo.llopis@tecnativa.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import logging

from odoo.tests.common import TransactionCase

_logger = logging.getLogger(__name__)


class ValueConversionCase(TransactionCase):
    def setUp(self):
        super(ValueConversionCase, self).setUp()
        self.agrolait = self.env.ref("base.res_partner_2")
        self.tpl = self.env.ref("base_custom_info.tpl_smart")
        self.prop_str = self.env.ref("base_custom_info.prop_teacher")
        self.prop_int = self.env.ref("base_custom_info.prop_haters")
        self.prop_float = self.env.ref("base_custom_info.prop_avg_note")
        self.prop_bool = self.env.ref("base_custom_info.prop_smartypants")
        self.prop_id = self.env.ref("base_custom_info.prop_weaknesses")

    def fill_value(self, prop, value, field="value"):
        """Create a custom info value."""
        _logger.info(
            "Creating. prop: %s; value: %s; field: %s", prop, value, field)
        self.agrolait.custom_info_template_id = self.tpl
        self.agrolait._onchange_custom_info_template_id()
        if field == "value":
            value = str(value)
        self.value = self.agrolait.get_custom_info_value(prop)
        self.value[field] = value

    def creation_found(self, value):
        """Ensure you can search what you just created."""
        prop = self.value.property_id
        _logger.info(
            "Searching. prop: %s; value: %s", prop, value)
        self.assertEqual(
            self.value.search([
                ("property_id", "=", prop.id),
                ("value", "=", value)]),
            self.value)
        self.assertEqual(
            self.value.search([
                ("property_id", "=", prop.id),
                ("value", "in", [value])]),
            self.value)
        self.assertIs(
            self.value.search([
                ("property_id", "=", prop.id),
                ("value", "not in", [value])]).id,
            False)

    def test_to_str(self):
        """Conversion to text."""
        self.fill_value(self.prop_str, "Mr. Einstein")
        self.creation_found("Mr. Einstein")
        self.assertEqual(self.value.value, self.value.value_str)

    def test_from_str(self):
        """Conversion from text."""
        self.fill_value(self.prop_str, "Mr. Einstein", "value_str")
        self.creation_found("Mr. Einstein")
        self.assertEqual(self.value.value, self.value.value_str)

    def test_to_int(self):
        """Conversion to whole number."""
        self.fill_value(self.prop_int, 5)
        self.creation_found("5")
        self.assertEqual(int(self.value.value), self.value.value_int)

    def test_from_int(self):
        """Conversion from whole number."""
        self.fill_value(self.prop_int, 5, "value_int")
        self.creation_found("5")
        self.assertEqual(int(self.value.value), self.value.value_int)

    def test_to_float(self):
        """Conversion to decimal number."""
        self.fill_value(self.prop_float, 9.5)
        self.creation_found("9.5")
        self.assertEqual(float(self.value.value), self.value.value_float)

    def test_from_float(self):
        """Conversion from decimal number."""
        self.fill_value(self.prop_float, 9.5, "value_float")
        self.creation_found("9.5")
        self.assertEqual(float(self.value.value), self.value.value_float)

    def test_to_bool_true(self):
        """Conversion to yes."""
        self.fill_value(self.prop_bool, "True")
        self.creation_found("True")
        self.assertEqual(self.value.with_context(lang="en_US").value, "Yes")
        self.assertIs(self.value.value_bool, True)

    def test_from_bool_true(self):
        """Conversion from yes."""
        self.fill_value(self.prop_bool, "True", "value_bool")
        self.creation_found("True")
        self.assertEqual(self.value.with_context(lang="en_US").value, "Yes")
        self.assertIs(self.value.value_bool, True)

    def test_to_bool_false(self):
        """Conversion to no."""
        self.fill_value(self.prop_bool, "False")
        self.assertEqual(self.value.with_context(lang="en_US").value, "No")
        self.assertIs(self.value.value_bool, False)

    def test_from_bool_false(self):
        """Conversion from no."""
        self.fill_value(self.prop_bool, False, "value_bool")
        self.assertEqual(self.value.with_context(lang="en_US").value, "No")
        self.assertIs(self.value.value_bool, False)

    def test_to_id(self):
        """Conversion to selection."""
        self.fill_value(self.prop_id, "Needs videogames")
        self.creation_found("Needs videogames")
        self.assertEqual(self.value.value, self.value.value_id.name)

    def test_from_id(self):
        """Conversion from selection."""
        self.fill_value(
            self.prop_id,
            self.env.ref("base_custom_info.opt_videogames").id,
            "value_id")
        self.creation_found("Needs videogames")
        self.assertEqual(self.value.value, self.value.value_id.name)
