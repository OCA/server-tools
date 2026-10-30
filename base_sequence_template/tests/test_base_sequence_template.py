# Copyright 2026 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseSequenceTemplate(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.model_company = cls.env["res.company"]
        cls.model_sequence_template = cls.env["ir.sequence.template"]
        cls.model_sequence = cls.env["ir.sequence"]
        cls.model_wizard = cls.env["generate.company.sequences.wizard"]

        cls.company_a = cls.model_company.create(
            {
                "name": "Company A",
                "phone": "12345",
            }
        )
        cls.company_b = cls.model_company.create(
            {
                "name": "Company B",
                "phone": "67890",
            }
        )
        cls.template = cls.model_sequence_template.create(
            {
                "name": "Test Template",
                "code": "test.sequence",
                "prefix": "/%(company_id.phone)s/",
                "suffix": "/%(year)s",
                "padding": 5,
                "number_increment": 1,
                "implementation": "no_gap",
            }
        )

    def _create_wizard(self, companies, templates):
        return self.model_wizard.create(
            {
                "company_ids": [(6, 0, companies.ids)],
                "template_ids": [(6, 0, templates.ids)],
            }
        )

    def test_extract_placeholders(self):
        # Extract only company_id placeholders
        wizard = self._create_wizard(self.company_a, self.template)
        placeholders = wizard._extract_placeholders("/%(company_id.phone)s/%(year)s")
        self.assertEqual(placeholders, {"company_id.phone"})

    def test_replace_company_placeholders(self):
        # Replace only company_id placeholders
        wizard = self._create_wizard(self.company_a, self.template)
        template = "/%(company_id.phone)s/%(year)s"
        values = {"company_id.phone": "12345"}
        result = wizard.replace_company_placeholders(template, values)
        self.assertEqual(result, "/12345/%(year)s")

    def test_action_generate_success(self):
        # Generate different companies' sequences, with the phone number
        wizard = self._create_wizard(self.company_a | self.company_b, self.template)
        wizard.action_generate()
        sequences = self.model_sequence.search(
            [
                ("code", "=", "test.sequence"),
                ("company_id", "in", (self.company_a | self.company_b).ids),
            ]
        )
        self.assertEqual(len(sequences), 2)
        seq_a = sequences.filtered(lambda s: s.company_id == self.company_a)
        seq_b = sequences.filtered(lambda s: s.company_id == self.company_b)
        # Phone number is correctly set in the prefix
        self.assertEqual(seq_a.prefix, "/12345/")
        self.assertEqual(seq_b.prefix, "/67890/")
        self.assertEqual(seq_a.suffix, "/%(year)s")
        self.assertEqual(seq_b.suffix, "/%(year)s")

    def test_missing_company_field_value(self):
        # Check that sequences are not generated if we use a company field
        # which is empty in any company
        template = self.model_sequence_template.create(
            {
                "name": "Missing Phone Template",
                "code": "missing.phone.seq",
                "prefix": "/%(company_id.phone)s/",
                "suffix": "",
                "padding": 3,
                "number_increment": 1,
                "implementation": "no_gap",
            }
        )
        company = self.model_company.create({"name": "No Phone Company"})
        wizard = self._create_wizard(company, template)
        with self.assertRaises(ValidationError):
            wizard.action_generate()

    def test_invalid_company_field_placeholder(self):
        # Check the sequences are not generated if we try to use an invalid
        # company field
        template = self.model_sequence_template.create(
            {
                "name": "Invalid Field Template",
                "code": "invalid.field.seq",
                "prefix": "/%(company_id.nonexistent_field)s/",
                "suffix": "",
                "padding": 3,
                "number_increment": 1,
                "implementation": "no_gap",
            }
        )
        wizard = self._create_wizard(self.company_a, template)
        with self.assertRaises(ValidationError):
            wizard.action_generate()
