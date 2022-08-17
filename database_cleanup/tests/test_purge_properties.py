# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import tagged

from .common import Common


# Use post_install to get all models loaded more info: odoo/odoo#13458
@tagged("post_install", "-at_install")
class TestCleanupPurgeLineProperty(Common):
    def setUp(self):
        super(TestCleanupPurgeLineProperty, self).setUp()
        # Create one property for tests
        self.partner_name_field_id = self.env["ir.model.fields"].search(
            [("name", "=", "name"), ("model_id.model", "=", "res.partner")], limit=1
        )

    def test_property_to_not_removed(self):
        self.property = self.env["ir.property"].create(
            {
                "fields_id": self.partner_name_field_id.id,
                "type": "char",
                "value_text": "My default partner name",
                "res_id": False,
            }
        )
        wizard = self.env["cleanup.purge.wizard.property"].create({})
        wizard.purge_all()
        self.assertTrue(self.property.exists())

    def test_property_no_value(self):
        self.property = self.env["ir.property"].create(
            {
                "fields_id": self.partner_name_field_id.id,
                "type": "char",
                "value_text": False,
                "res_id": False,
            }
        )
        wizard = self.env["cleanup.purge.wizard.property"].create({})
        wizard.purge_all()
        self.assertFalse(self.property.exists())
