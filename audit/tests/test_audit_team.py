"""Tests for `audit.team`."""

import uuid

import psycopg2.errors

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("audit_models", "audit_model_team")
class TestAuditTeam(TransactionCase):
    """Tests for ``audit.team`` (``models/audit_team.py``)."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.inspector_a = cls.env["audit.inspector"].create({"name": "Member A"})
        cls.inspector_b = cls.env["audit.inspector"].create({"name": "Leader B"})

    def test_team_name_must_be_unique(self):
        name = f"North Island {uuid.uuid4().hex}"
        self.env["audit.team"].create({"name": name})
        try:
            self.env["audit.team"].create({"name": name})
        except (ValidationError, psycopg2.errors.UniqueViolation):
            return
        self.fail("expected duplicate team name to be rejected")

    def test_members_and_leaders_many2many(self):
        team = self.env["audit.team"].create(
            {
                "name": "Field Team 1",
                "team_member_ids": [(6, 0, [self.inspector_a.id])],
                "team_leader_ids": [(6, 0, [self.inspector_b.id])],
            }
        )
        self.assertIn(self.inspector_a, team.team_member_ids)
        self.assertIn(self.inspector_b, team.team_leader_ids)
