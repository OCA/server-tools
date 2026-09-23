# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class JsonExportTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        # Create ir.exports + lines for res.partner
        cls.partner_exporter = cls.env["ir.exports"].create(
            {
                "name": "Test Partner Export",
                "resource": "res.partner",
            }
        )
        for field_name in ["name", "email", "phone"]:
            cls.env["ir.exports.line"].create(
                {
                    "export_id": cls.partner_exporter.id,
                    "name": field_name,
                }
            )
        # Relational line
        cls.env["ir.exports.line"].create(
            {
                "export_id": cls.partner_exporter.id,
                "name": "country_id/name",
            }
        )

        # Create schema
        cls.partner_model = cls.env.ref("base.model_res_partner")
        cls.schema = cls.env["json.export.schema"].create(
            {
                "name": "Test Partners",
                "model_id": cls.partner_model.id,
                "exporter_id": cls.partner_exporter.id,
                "domain": "[]",
                "record_limit": 10,
                "include_record_id": True,
                "preview_count": 3,
            }
        )

        # Create test partners
        country_us = cls.env.ref("base.us")
        cls.partner1 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 1",
                "email": "test1@example.com",
                "phone": "+1234567890",
                "country_id": country_us.id,
            }
        )
        cls.partner2 = cls.env["res.partner"].create(
            {
                "name": "Test Partner 2",
                "email": "test2@example.com",
            }
        )
