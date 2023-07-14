# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestBaseTranslationFieldLabel(TransactionCase):
    def setUp(self):
        super().setUp()
        # Models
        self.translation_model = self.env["ir.translation"]
        self.partner_model = self.env["res.partner"]

        # Set up
        self.translation_model._load_module_terms(["base"], ["ca_ES"])

        # Instances
        self.parent_partner = self.partner_model.create({"name": "Parent Partner"})
        self.child_partner = self.partner_model.create(
            {"name": "Child Partner", "parent_id": self.parent_partner.id}
        )
        self.translated_term = self.translation_model.create(
            {
                "type": "model",
                "name": "res.partner,parent_id",
                "module": "base",
                "lang": "ca_ES",
                "res_id": self.child_partner.id,
                "value": "Companyia Relacionada",
                "state": "translated",
            }
        )

    def test_01_check_field_label(self):
        """
        Check that the field label of the translated term matches the string set on the
        Odoo field.
        """
        self.assertEqual(
            self.translated_term.field_label,
            "Related Company",
            "Field Label on the translated term should match the string value on the "
            "Odoo field.",
        )
