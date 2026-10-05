# Copyright 2025 Dynapps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from unittest.mock import MagicMock, patch

from odoo.tests import common


class TestAuditlogHTTPRequest(common.TransactionCase):
    """Tests for auditlog.http.request model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.request_model = cls.env["auditlog.http.request"]
        cls.session_model = cls.env["auditlog.http.session"]

    # -------------------------------------------------------------------------
    # Base Scenarios
    # -------------------------------------------------------------------------

    def test_no_request_returns_false(self):
        """When no HTTP request object exists, should return False."""
        with patch("odoo.addons.auditlog.models.auditlog_http_request.request", None):
            result = self.request_model.current_http_request()
            self.assertFalse(
                result,
                "Expected False when no HTTP request object is present",
            )

    def test_no_httprequest_returns_false(self):
        """When request exists but has no httprequest, should return False."""
        mock_request = MagicMock()
        mock_request.httprequest = None
        mock_request.env = self.env

        with patch(
            "odoo.addons.auditlog.models.auditlog_http_request.request", mock_request
        ):
            result = self.request_model.current_http_request()
            self.assertFalse(
                result,
                "Expected False when request.httprequest is missing",
            )

    # -------------------------------------------------------------------------
    # Existing HTTP Request Reused
    # -------------------------------------------------------------------------

    def test_existing_http_request_reused(self):
        """Should return same ID if auditlog_http_request_id already set."""
        mock_httprequest = MagicMock()
        mock_httprequest.path = "/web"
        mock_httprequest.url_root = "http://localhost/"
        mock_httprequest.auditlog_http_request_id = None

        mock_request = MagicMock()
        mock_request.httprequest = mock_httprequest
        mock_request.env = self.env

        # Create an existing HTTP request record manually
        existing = self.request_model.create(
            {
                "name": "/web",
                "root_url": "http://localhost/",
                "user_id": self.env.uid,
            }
        )
        mock_httprequest.auditlog_http_request_id = existing.id

        # Patch DB fetch to simulate record exists
        with (
            patch(
                "odoo.addons.auditlog.models.auditlog_http_request.request",
                mock_request,
            ),
            patch.object(self.env.cr, "fetchone", return_value=(existing.id,)),
        ):
            result = self.request_model.current_http_request()

        self.assertEqual(
            result,
            existing.id,
            "Should return the existing HTTP request ID if already present",
        )

    # -------------------------------------------------------------------------
    # New HTTP Request Created
    # -------------------------------------------------------------------------

    def test_new_http_request_created(self):
        """Should create a new HTTP request record when none exists."""
        mock_httprequest = MagicMock()
        mock_httprequest.path = "/web/login"
        mock_httprequest.url_root = "http://localhost/"
        mock_httprequest.auditlog_http_request_id = None

        mock_request = MagicMock()
        mock_request.httprequest = mock_httprequest
        mock_request.env = self.env(context={"lang": "en_US"})

        with (
            patch(
                "odoo.addons.auditlog.models.auditlog_http_request.request",
                mock_request,
            ),
            patch(
                "odoo.addons.auditlog.models.auditlog_http_session.AuditlogHTTPSession.current_http_session",
                return_value=None,
            ),
        ):
            http_request_id = self.request_model.current_http_request()

        created = self.request_model.browse(http_request_id)
        self.assertTrue(
            created.exists(), "Expected a new HTTP request record to be created"
        )
        self.assertEqual(
            created.name, "/web/login", "Path should match httprequest.path"
        )
        self.assertEqual(
            created.root_url,
            "http://localhost/",
            "Root URL should match httprequest.url_root",
        )
        self.assertEqual(
            created.user_id.id, self.env.uid, "User should match request.env.uid"
        )
        self.assertIn(
            "'lang': 'en_US'",
            created.user_context,
            "Context string should include language key",
        )
        self.assertTrue(
            created.display_name.startswith("/web/login"),
            "Display name should start with the HTTP path",
        )

    # -------------------------------------------------------------------------
    # Integration with HTTP Session
    # -------------------------------------------------------------------------

    def test_http_request_links_to_session(self):
        """Should link the HTTP request to a valid HTTP session."""
        mock_httprequest = MagicMock()
        mock_httprequest.path = "/test/path"
        mock_httprequest.url_root = "http://testserver/"
        mock_httprequest.auditlog_http_request_id = None

        mock_request = MagicMock()
        mock_request.httprequest = mock_httprequest
        mock_request.env = self.env

        session = self.session_model.create(
            {
                "name": "SESSION456",
                "user_id": self.env.uid,
            }
        )

        with (
            patch(
                "odoo.addons.auditlog.models.auditlog_http_request.request",
                mock_request,
            ),
            patch(
                "odoo.addons.auditlog.models.auditlog_http_session.AuditlogHTTPSession.current_http_session",
                return_value=session.id,
            ),
        ):
            http_request_id = self.request_model.current_http_request()

        self.assertEqual(
            self.request_model.browse(http_request_id).http_session_id,
            session,
            "The created HTTP request should be linked to the given session",
        )
