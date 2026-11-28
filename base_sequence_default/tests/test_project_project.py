# Copyright 2023 Moduon Team S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)


from odoo.tests.common import TransactionCase

from ..models.base import SEQUENCE_PREFIX


class BaseSequenceDefaultCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        is_model = cls.env["ir.sequence"]
        cls.partner_seqs = is_model.create(
            [
                {
                    "name": "Partner name",
                    "code": f"{SEQUENCE_PREFIX}.res.partner.fields.name",
                    "implementation": "standard",
                    "prefix": "PN/",
                    "padding": 3,
                    "number_increment": 1,
                },
                {
                    "name": "Partner mobile... let's spam all Spaniards",
                    "code": f"{SEQUENCE_PREFIX}.res.partner.fields.mobile",
                    "implementation": "standard",
                    "prefix": "+34 ",
                    "padding": 9,
                    "number_increment": 1,
                },
            ]
        )

    def test_partner_default_field(self):
        """Test that new created partner has the correct default field values."""
        partner = self.env["res.partner"].create({"name": "-"})
        self.assertEqual(partner.name, "PN/001")
        self.assertEqual(partner.mobile, "+34 000000001")
