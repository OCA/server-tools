from odoo.addons.base.tests.common import BaseCommon


class TestMailTracking(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.MailTracking = cls.env["mail.tracking.value"]

    def test_create_tracking_values_html(self):
        initial_value = "<p>Initial Value</p>"
        new_value = "<p>New Value</p>"
        col_name = "comment"
        col_info = {"type": "html"}
        record = self.env["res.partner"].create({"name": "Test Partner"})

        values = self.MailTracking._create_tracking_values(
            initial_value, new_value, col_name, col_info, record
        )

        self.assertEqual(values["old_value_char"], "Initial Value")
        self.assertEqual(values["new_value_char"], "New Value")
