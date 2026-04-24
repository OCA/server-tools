"""Tests for `audit.snapshot` and related records."""

import json

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("audit_models", "audit_model_snapshot")
class TestAuditSnapshot(TransactionCase):
    """Tests for snapshot models in ``models/audit_snapshot.py``."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.domain = cls.env["audit.domain"].create({"name": "Snapshot Domain"})
        cls.section = cls.env["audit.section"].create(
            {"name": "Snap Section", "domain_id": cls.domain.id}
        )
        cls.question = cls.env["audit.question"].create(
            {
                "prompt": "Is it clean?",
                "answer_type": "boolean",
                "section_id": cls.section.id,
            }
        )
        cls.target = cls.env["audit.target"].create(
            {"name": "Snapshot Target", "domain_id": cls.domain.id}
        )
        cls.inspector = cls.env["audit.inspector"].create({"name": "Snap Inspector"})
        cls.env["audit.team"].create({"name": "Snapshot Team"})

    def test_snapshot_question_compute_value_boolean_and_star(self):
        ss = self.env["audit.snapshot_section"].create(
            {
                "name": "S",
                "domain_id": self.domain.id,
            }
        )
        sq = self.env["audit.snapshot_question"].create(
            {
                "snapshot_section_id": ss.id,
                "answer_type": "boolean",
                "answer_yn": "1",
                "answer_star": "4",
                "answer_perc": 0.0,
            }
        )
        self.assertAlmostEqual(sq.value, 1.0 + 1.0 + 0.0)

    def test_snapshot_question_toggle_not_applicable(self):
        ss = self.env["audit.snapshot_section"].create(
            {"name": "S2", "domain_id": self.domain.id}
        )
        sq = self.env["audit.snapshot_question"].create(
            {
                "snapshot_section_id": ss.id,
                "answer_type": "boolean",
                "applicable": True,
            }
        )
        out = self.env["audit.snapshot_question"].toggle_not_applicable(sq.id)
        self.assertFalse(out["applicable"])
        out2 = self.env["audit.snapshot_question"].toggle_not_applicable(sq.id)
        self.assertTrue(out2["applicable"])

    def test_snapshot_section_scores(self):
        snap = self.env["audit.snapshot"].create(
            {
                "domain_id": self.domain.id,
                "target_id": self.target.id,
                "inspector_id": self.inspector.id,
            }
        )
        section = snap.snapshot_section_ids[0]
        questions = section.snapshot_question_ids
        self.assertTrue(questions)
        questions.write(
            {
                "answer_yn": "1",
                "answer_star": "4",
                "answer_perc": 0.0,
            }
        )
        section.invalidate_recordset()
        self.assertGreater(section.maximum_section_score, 0)
        self.assertGreater(section.actual_section_score, 0)
        self.assertGreaterEqual(section.percentage_section_score, 0.0)

    def test_snapshot_create_requires_domain_target_inspector(self):
        with self.assertRaises(UserError):
            self.env["audit.snapshot"].create(
                {
                    "domain_id": self.domain.id,
                    "target_id": self.target.id,
                }
            )

    def test_snapshot_compute_name(self):
        snap = self.env["audit.snapshot"].create(
            {
                "domain_id": self.domain.id,
                "target_id": self.target.id,
                "inspector_id": self.inspector.id,
            }
        )
        self.assertIn(self.target.name, snap.name)

    def test_get_snapshot_questions_structure(self):
        snap = self.env["audit.snapshot"].create(
            {
                "domain_id": self.domain.id,
                "target_id": self.target.id,
                "inspector_id": self.inspector.id,
            }
        )
        data = snap.get_snapshot_questions()
        self.assertIn("sections", data)
        self.assertIn("questions", data)
        self.assertEqual(data["all_locked"], snap.locked)

    def test_custom_search_minimal_json_admin(self):
        payload = json.dumps({"searchPage": 1})
        result = self.env["audit.snapshot"].custom_search(payload)
        self.assertIn("snapshots", result)
        self.assertIn("numberOfPages", result)
        self.assertIn("newPageNumber", result)
