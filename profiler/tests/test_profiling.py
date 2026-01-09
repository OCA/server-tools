# Copyright 2018 Vauxoo (https://www.vauxoo.com) <info@vauxoo.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest.mock import MagicMock, patch

import odoo.http
from odoo.tests.common import HttpCase, at_install, get_db_name, post_install


@at_install(False)
@post_install(True)
class TestProfiling(HttpCase):
    def test_profile_creation(self):
        """We are testing the creation of a profile."""
        prof_obj = self.env["profiler.profile"]
        profile = prof_obj.create(
            {"name": "this_profiler", "enable_python": True, "python_method": "full"}
        )
        self.assertEqual(0, profile.attachment_count)
        profile.enable()
        self.assertFalse(
            self.xmlrpc_common.authenticate(
                self.env.cr.dbname, "this is not a user", "this is not a password", {}
            )
        )
        profile.disable()

    def test_profile_creation_with_py(self):
        """We are testing the creation of a profile. with py index"""
        prof_obj = self.env["profiler.profile"]
        profile = prof_obj.create(
            {
                "name": "this_profiler",
                "enable_python": True,
                "use_py_index": True,
                "python_method": "full",
            }
        )
        self.assertEqual(0, profile.attachment_count)
        profile.enable()
        self.assertFalse(
            self.xmlrpc_common.authenticate(
                self.env.cr.dbname, "this is not a user", "this is not a password", {}
            )
        )
        profile.disable()

    def test_onchange(self):
        prof_obj = self.env["profiler.profile"]
        profile = prof_obj.create({"name": "this_profiler"})
        self.assertFalse(profile.description)
        profile.enable_postgresql = True
        profile.onchange_enable_postgresql()
        self.assertTrue(profile.description)
        profile.enable()
        self.assertFalse(
            self.xmlrpc_common.authenticate(
                self.env.cr.dbname, "this is not a user", "this is not a password", {}
            )
        )
        profile.disable()

    def test_profile_creation_http(self):
        """We are testing the creation of a profile based on HTTP calls."""
        db = get_db_name()
        session_id = "1234567890"
        admin_user = self.env.ref("base.user_admin")
        password = "admin"
        uid = admin_user.id
        with patch("odoo.http.request") as request:
            request.uid = uid
            request.httprequest = MagicMock()
            request.httprequest.session.sid = session_id
            request.httprequest.url_root = "http://localhost:8069"
            request.httprequest.path = "/test_url"
            request.env = self.env
            request.context = self.env.context
            prof_obj = self.env["profiler.profile"]
            profile = prof_obj.create(
                {
                    "name": "this_http_profiler",
                    "enable_python": True,
                    "python_method": "request",
                }
            )
            profile.enable()
            self.assertEqual(profile.session, session_id)
            profiler_id = profile.id
            odoo.http.dispatch_rpc(
                "object",
                "execute_kw",
                (db, uid, password, "profiler.profile", "read", [profiler_id]),
            )
            profile.disable()
            self.assertEqual(len(profile.sudo().py_request_lines), 1)
            self.assertTrue(profile.py_request_lines.display_name)
            self.assertTrue(profile.py_request_lines.attachment_id)
            profile.action_view_attachment()
