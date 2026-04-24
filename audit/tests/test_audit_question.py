"""Tests for `audit.question`."""

import psycopg2.errors

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("audit_models", "audit_model_question")
class TestAuditQuestion(TransactionCase):
    """Tests for ``audit.question`` (``models/audit_question.py``)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.domain = cls.env["audit.domain"].create({"name": "Question Test Domain"})
        cls.section = cls.env["audit.section"].create(
            {"name": "Section A", "domain_id": cls.domain.id}
        )

    def test_name_follows_prompt(self):
        prompt = "Is the emergency exit clear?"
        question = self.env["audit.question"].create(
            {
                "prompt": prompt,
                "answer_type": "boolean",
                "section_id": self.section.id,
            }
        )
        self.assertEqual(question.name, prompt)

    def test_required_answer_type(self):
        with self.assertRaises(psycopg2.errors.NotNullViolation):
            self.env["audit.question"].create(
                {"prompt": "Missing type", "section_id": self.section.id}
            )
