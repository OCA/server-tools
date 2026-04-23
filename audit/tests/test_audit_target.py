# -*- coding: utf-8 -*-
"""Tests for `audit.target`."""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


@tagged("audit_models", "audit_model_target")
class TestAuditTarget(TransactionCase):
    """Tests for ``audit.target`` and ``audit.domain_target_rel`` (``models/audit_target.py``)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.domain = cls.env["audit.domain"].create({"name": "Target Test Domain"})

    def test_duplicate_target_name_rejected_on_create(self):
        self.env["audit.target"].create(
            {"name": "Same Name Store", "domain_id": self.domain.id}
        )
        with self.assertRaises(ValidationError):
            self.env["audit.target"].create(
                {"name": "Same Name Store", "domain_id": self.domain.id}
            )

    def test_create_sets_domain_id_from_all_domain_rel_ids(self):
        other = self.env["audit.domain"].create({"name": "Secondary Domain"})
        target = self.env["audit.target"].create(
            {
                "name": "Target with rel domains",
                "all_domain_rel_ids": [(6, 0, [other.id])],
            }
        )
        self.assertEqual(target.domain_id, other)

    def test_link_to_domain_creates_relation_once(self):
        target = self.env["audit.target"].create(
            {"name": "Linkable", "domain_id": self.domain.id}
        )
        target.link_to_domain(self.domain.id, target.id)
        rel = self.env["audit.domain_target_rel"].search(
            [
                ("domain_id", "=", self.domain.id),
                ("target_id", "=", target.id),
            ]
        )
        self.assertTrue(rel)
        target.link_to_domain(self.domain.id, target.id)
        self.assertEqual(
            len(
                self.env["audit.domain_target_rel"].search(
                    [
                        ("domain_id", "=", self.domain.id),
                        ("target_id", "=", target.id),
                    ]
                )
            ),
            1,
        )

    def test_write_rejects_duplicate_name(self):
        self.env["audit.target"].create(
            {"name": "Alpha", "domain_id": self.domain.id}
        )
        beta = self.env["audit.target"].create(
            {"name": "Beta", "domain_id": self.domain.id}
        )
        with self.assertRaises(ValidationError):
            beta.write({"name": "Alpha"})
