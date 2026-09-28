"""Tests for `audit.section`."""

import psycopg2.errors

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


@tagged("audit_models", "audit_model_section")
class TestAuditSection(TransactionCase):
    """Tests for ``audit.section`` (``models/audit_section.py``)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.domain = cls.env["audit.domain"].create({"name": "Section Test Domain"})

    def test_create_section_linked_to_domain(self):
        section = self.env["audit.section"].create(
            {"name": "Opening checks", "domain_id": self.domain.id}
        )
        self.assertEqual(section.domain_id, self.domain)

    def test_domain_id_required(self):
        with (
            mute_logger("odoo.sql_db"),
            self.assertRaises(psycopg2.errors.NotNullViolation),
        ):
            self.env["audit.section"].create({"name": "Orphan section"})
