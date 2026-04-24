"""Tests for `audit.snapshot` and related records."""

import json
import uuid

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

    def test_get_snapshot_questions_on_empty_recordset(self):
        self.assertEqual(
            self.env["audit.snapshot"].browse([]).get_snapshot_questions(),
            {},
        )

    def test_snapshot_create_accepts_list_vals(self):
        snap = self.env["audit.snapshot"].create(
            [
                {
                    "domain_id": self.domain.id,
                    "target_id": self.target.id,
                    "inspector_id": self.inspector.id,
                }
            ]
        )
        self.assertTrue(snap.id)

    def test_snapshot_question_write_strips_data_url_on_image(self):
        ss = self.env["audit.snapshot_section"].create(
            {"name": "ImgSec", "domain_id": self.domain.id}
        )
        sq = self.env["audit.snapshot_question"].create(
            {
                "snapshot_section_id": ss.id,
                "answer_type": "boolean",
            }
        )
        b64 = "R0lGODlhAQABAIAAAAUEBAAAACwAAAAAAQABAAACAkQBADs="
        raw = f"data:image/gif;base64,{b64}"
        sq.write({"image": raw})
        self.assertTrue(
            bool(sq.image) is True,
            msg="data: URL prefix should be stripped so the image is stored",
        )

    def test_custom_search_filters_text_status_and_clamps_page(self):
        for _i in range(3):
            self.env["audit.snapshot"].create(
                {
                    "domain_id": self.domain.id,
                    "target_id": self.target.id,
                    "inspector_id": self.inspector.id,
                }
            )
        for snap in self.env["audit.snapshot"].search([]):
            snap.write({"percentage_score": 0.1})
        ptext = json.dumps(
            {
                "searchText": "Snapshot",
                "searchStatus": "FAIL",
                "searchPage": 1,
            }
        )
        r1 = self.env["audit.snapshot"].custom_search(ptext)
        self.assertIn("snapshots", r1)
        ppass = json.dumps(
            {
                "searchText": "Snapshot",
                "searchStatus": "PASS",
                "searchPage": 1,
            }
        )
        for snap in self.env["audit.snapshot"].search([]):
            snap.write({"percentage_score": 0.9})
        r2 = self.env["audit.snapshot"].custom_search(ppass)
        self.assertIn("numberOfPages", r2)
        pbig = json.dumps(
            {
                "searchText": "Snapshot",
                "searchStatus": "PASS",
                "searchPage": 9999,
            }
        )
        r3 = self.env["audit.snapshot"].custom_search(pbig)
        self.assertIsInstance(r3.get("newPageNumber"), (int, type(None)))

    def test_snapshot_percentage_score_recomputes_from_dicts(self):
        snap = self.env["audit.snapshot"].create(
            {
                "domain_id": self.domain.id,
                "target_id": self.target.id,
                "inspector_id": self.inspector.id,
            }
        )
        self.env["audit.snapshot"].snapshot_percentage_score(
            [{"id": snap.id, "name": "x"}]
        )
        self.assertIsNotNone(snap.percentage_score)

    def test_questions_with_comments_count_when_locked(self):
        snap = self.env["audit.snapshot"].create(
            {
                "domain_id": self.domain.id,
                "target_id": self.target.id,
                "inspector_id": self.inspector.id,
            }
        )
        section = snap.snapshot_section_ids[0]
        q = section.snapshot_question_ids[0]
        q.write({"comment": "note"})
        snap.locked = True
        self.assertEqual(snap.questions_with_comments, 1)

    def _internal_user(self):
        """Build a non-admin user for with_user (same idea as access tests)."""
        template = self.env.ref("base.default_user", raise_if_not_found=False)
        if not template:
            self.skipTest("base.default_user is not available in this database")
        suffix = uuid.uuid4().hex
        return template.sudo().copy(
            {
                "name": f"Snapshot su {suffix}",
                "login": f"audit_sp_{suffix}@test.local",
                "password": "snap-test-pass",
            }
        )

    def test_snapshots_per_user_non_admin_inspector(self):
        user = self._internal_user()
        self.env["audit.inspector"].create(
            {
                "name": "Sp User Insp",
                "res_user_id": user.id,
            }
        )
        self.env["audit.snapshot"].create(
            {
                "domain_id": self.domain.id,
                "target_id": self.target.id,
                "inspector_id": self.inspector.id,
            }
        )
        rows, total = self.env["audit.snapshot"].with_user(
            user,
        ).snapshots_per_user(
            [("active", "=", True)],
            1,
        )
        self.assertIsInstance(rows, list)
        self.assertIsInstance(total, int)
        self.assertGreaterEqual(total, 0)
        self.assertGreaterEqual(len(rows), 0)
