# -*- coding: utf-8 -*-
"""Tests for `audit.domain` and domain duplication."""
import uuid

import psycopg2.errors

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


@tagged("audit_models", "audit_model_domain")
class TestAuditDomain(TransactionCase):
    """Tests for ``audit.domain`` (``models/audit_domain.py``)."""

    def test_domain_name_unique(self):
        name = f"Unique Domain {uuid.uuid4().hex}"
        self.env["audit.domain"].create({"name": name})
        try:
            self.env["audit.domain"].create({"name": name})
        except (ValidationError, psycopg2.errors.UniqueViolation):
            return
        self.fail("expected duplicate domain name to be rejected")

    def test_compute_all_target_rel_ids_merges_one2many_and_many2many(self):
        domain = self.env["audit.domain"].create({"name": "Merge Targets Domain"})
        t_primary = self.env["audit.target"].create(
            {"name": "Primary target", "domain_id": domain.id}
        )
        t_extra = self.env["audit.target"].create({"name": "Extra target"})
        domain.target_rel_ids = [(6, 0, [t_extra.id])]
        domain.invalidate_recordset()
        self.assertIn(t_primary, domain.all_target_rel_ids)
        self.assertIn(t_extra, domain.all_target_rel_ids)

    def test_action_duplicate_domain_creates_copy_with_sections_and_questions(self):
        domain = self.env["audit.domain"].create({"name": "Original Domain For Dup"})
        section = self.env["audit.section"].create(
            {"name": "Sec", "domain_id": domain.id}
        )
        self.env["audit.question"].create(
            {
                "prompt": "Dup Q",
                "answer_type": "integer",
                "section_id": section.id,
            }
        )
        action = domain.action_duplicate_domain()
        self.assertEqual(action.get("type"), "ir.actions.client")
        new_domains = self.env["audit.domain"].search(
            [("name", "ilike", "Original Domain For Dup - Duplicate_")]
        )
        self.assertEqual(len(new_domains), 1)
        self.assertTrue(new_domains.section_ids)
        self.assertTrue(new_domains.section_ids.question_ids)
