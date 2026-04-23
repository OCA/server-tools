# -*- coding: utf-8 -*-
"""Tests for `audit.inspector`."""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("audit_models", "audit_model_inspector")
class TestAuditInspector(TransactionCase):
    """Tests for ``audit.inspector`` (``models/audit_inspector.py``)."""

    def test_full_name_from_partner_name(self):
        partner = self.env["res.partner"].create({"name": "Ada Lovelace"})
        inspector = self.env["audit.inspector"].create(
            {"name": "Inspector record", "partner_id": partner.id},
        )
        self.assertEqual(inspector.full_name, "Ada Lovelace")

    def test_full_name_from_forename_surname(self):
        inspector = self.env["audit.inspector"].create(
            {
                "name": "Fallback",
                "forename": "Grace",
                "surname": "Hopper",
            }
        )
        self.assertEqual(inspector.full_name, "Grace Hopper")

    def test_create_without_partner_builds_name_from_parts(self):
        inspector = self.env["audit.inspector"].create(
            {"forename": "Alan", "surname": "Turing"},
        )
        self.assertEqual(inspector.name, "Alan Turing")

    def test_create_without_partner_uses_generic_when_no_parts(self):
        inspector = self.env["audit.inspector"].create({})
        self.assertEqual(inspector.name, "Inspector")
