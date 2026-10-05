# Copyright 2025 Dynapps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import MagicMock, patch

from odoo.tests import common


class TestAuditlogHTTPSession(common.TransactionCase):
    """Tests for auditlog.http.session model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.session_model = cls.env["auditlog.http.session"]

    # -------------------------------------------------------------------------
    # Base Scenarios
    # -------------------------------------------------------------------------

    def test_no_request_returns_false(self):
        """When no HTTP request object exists, should return False."""
        with patch("odoo.addons.auditlog.models.auditlog_http_session.request", None):
            result = self.session_model.current_http_session()
            self.assertFalse(
                result,
                "Expected False when no HTTP request object is present",
            )

    def test_no_httpsession_returns_false(self):
        """When request exists but has no session, should return False."""
        mock_request = MagicMock()
        mock_request.env = self.env
        mock_request.session = None
        with patch(
            "odoo.addons.auditlog.models.auditlog_http_session.request", mock_request
        ):
            result = self.session_model.current_http_session()
            self.assertFalse(
                result,
                "Expected False when HTTP request has no session object",
            )

    # -------------------------------------------------------------------------
    # Existing Session
    # -------------------------------------------------------------------------

    def test_existing_session_reused(self):
        """Should return the existing session ID if already logged."""
        mock_request = MagicMock()
        mock_request.env = self.env
        mock_request.session.sid = "SESSION123"

        # Create an existing record to be reused
        existing = self.session_model.create(
            {
                "name": "SESSION123",
                "user_id": self.env.uid,
            }
        )

        with patch(
            "odoo.addons.auditlog.models.auditlog_http_session.request", mock_request
        ):
            result = self.session_model.current_http_session()

        self.assertEqual(
            result,
            existing.id,
            "Should return the ID of the existing session log",
        )

    # -------------------------------------------------------------------------
    # New Session
    # -------------------------------------------------------------------------

    def test_new_session_created(self):
        """Should create and return a new session record when none exists."""
        mock_request = MagicMock()
        mock_request.env = self.env
        mock_request.session.sid = "NEWSESSION456"

        with patch(
            "odoo.addons.auditlog.models.auditlog_http_session.request", mock_request
        ):
            result = self.session_model.current_http_session()

        created = self.session_model.browse(result)
        self.assertTrue(created.exists(), "Expected a new session record to be created")
        self.assertEqual(created.name, "NEWSESSION456", "Session ID should match SID")
        self.assertEqual(
            created.user_id.id, self.env.uid, "User should match request.env.uid"
        )
        self.assertEqual(
            created.display_name.split(" ")[0],
            self.env.user.name,
            "Display name should include user name",
        )

    # -------------------------------------------------------------------------
    # Edge Case: Different User Same Session ID
    # -------------------------------------------------------------------------

    def test_same_sid_different_user_creates_new(self):
        """A session with same SID but different user should create new log."""
        user2 = self.env["res.users"].create(
            {
                "name": "User2",
                "login": "user2@example.com",
            }
        )

        # Existing record with same SID but another user
        self.session_model.create(
            {
                "name": "SID_DUPLICATE",
                "user_id": user2.id,
            }
        )

        mock_request = MagicMock()
        mock_request.env = self.env
        mock_request.session.sid = "SID_DUPLICATE"

        with patch(
            "odoo.addons.auditlog.models.auditlog_http_session.request", mock_request
        ):
            result = self.session_model.current_http_session()

        created = self.session_model.browse(result)
        self.assertNotEqual(
            created.user_id.id,
            user2.id,
            "New session should be created for a different user even if SID matches",
        )
