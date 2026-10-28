# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.tests.common import tagged

from odoo.addons.base.tests.common import BaseCommon


@tagged("post_install", "-at_install")
class TestMailTracking(BaseCommon):
    _test_user_groups = ("base.group_system",)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_create_tracking_values_html(self):
        initial_value = "<p>Initial Value</p>"
        new_value = "<p>New Value</p>"
        col_name = "comment"
        col_info = {"type": "html"}

        values = self.partner._create_mail_tracking_values(
            initial_value, new_value, col_name, col_info
        )

        self.assertEqual(values["old_value_char"], "Initial Value")
        self.assertEqual(values["new_value_char"], "New Value")
        self.assertEqual(values["field_label"], "Notes")

        values_with_string = self.partner._create_mail_tracking_values(
            initial_value,
            new_value,
            col_name,
            {"type": "html", "string": "Custom Notes"},
        )
        self.assertEqual(values_with_string["field_label"], "Custom Notes")

    def test_create_tracking_values_unsupported(self):
        col_name = "image_1920"
        col_info = {"type": "binary"}
        with self.assertRaises(NotImplementedError):
            self.partner._create_mail_tracking_values(
                False, b"data", col_name, col_info
            )
