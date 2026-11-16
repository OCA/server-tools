import base64
from datetime import timedelta
from unittest.mock import MagicMock, patch

from odoo import fields
from odoo.exceptions import AccessError
from odoo.modules.module import get_module_path
from odoo.tests.common import TransactionCase, new_test_user
from odoo.tools import mute_logger

REQUESTS_GET = "odoo.addons.issue_auto_send.models.res_company.requests.get"
REQUESTS_POST = "odoo.addons.issue_auto_send.models.res_company.requests.post"
REQUESTS_PUT = "odoo.addons.issue_auto_send.models.res_company.requests.put"
MASK = "*" * 8
MODEL_LOGGER = "odoo.addons.issue_auto_send.models.res_company"


class TestIssueAutoSend(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_id = cls.env.company
        cls.company_id.write(
            {
                "issue_auto_send_github_url": "https://github.com/weinni2000/error_logs_test",
                "issue_auto_send_github_user": "weinni2000-spezi",
                "issue_auto_send_github_token": "test-token",
                "issue_auto_send_skip_duplicates": False,
            }
        )

    def _issue_response(self, number=1):
        response = MagicMock(status_code=201)
        response.json.return_value = {
            "html_url": f"https://github.com/weinni2000/error_logs_test/issues/{number}"
        }
        return response

    def _send(self, **kwargs):
        kwargs.setdefault("name", "Odoo Server Error")
        kwargs.setdefault("traceback", "Traceback")
        return self.env["res.company"].action_send_github_issue(**kwargs)

    def test_automatic_send_disabled(self):
        self.company_id.issue_auto_send_enabled = False
        with patch(REQUESTS_POST) as mock_post:
            result = self._send(automatic=True)
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "disabled")
        mock_post.assert_not_called()

    def test_manual_send_with_auto_send_disabled(self):
        self.company_id.issue_auto_send_enabled = False
        with patch(REQUESTS_POST, return_value=self._issue_response(2)) as mock_post:
            result = self._send()
        self.assertTrue(result["ok"])
        mock_post.assert_called_once()

    def test_send_missing_token(self):
        self.company_id.write(
            {
                "issue_auto_send_enabled": True,
                "issue_auto_send_github_token": False,
            }
        )
        result = self._send()
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "missing_token")

    def test_send_enabled(self):
        self.company_id.issue_auto_send_enabled = True
        with patch(REQUESTS_POST, return_value=self._issue_response()) as mock_post:
            result = self._send(
                message="password=super-secret",
                traceback="Traceback with access_token=token-secret",
                context_details="session_id=session-secret",
            )
        self.assertTrue(result["ok"])
        self.assertEqual(
            result["issue_url"],
            "https://github.com/weinni2000/error_logs_test/issues/1",
        )
        url = mock_post.call_args.args[0]
        self.assertEqual(
            url, "https://api.github.com/repos/weinni2000/error_logs_test/issues"
        )
        headers = mock_post.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(headers["User-Agent"], "weinni2000-spezi")
        body = mock_post.call_args.kwargs["json"]["body"]
        self.assertIn("### Environment", body)
        self.assertIn("### Structured Context", body)
        self.assertIn("Traceback", body)
        self.assertIn(f"password={MASK}", body)
        self.assertIn(f"access_token={MASK}", body)
        self.assertIn(f"session_id={MASK}", body)
        self.assertNotIn("super-secret", body)
        self.assertNotIn("token-secret", body)
        self.assertNotIn("session-secret", body)

    def test_mask_authorization_and_credentials(self):
        company_id = self.company_id.sudo()
        cases = {
            "Authorization: Bearer abcdef123456": "abcdef123456",
            "headers={'Authorization': 'Basic dXNlcjpwYXNz'}": "dXNlcjpwYXNz",
            '{"password": "hunter22", "login": "admin"}': "hunter22",
            "requests.get('https://bot:s3cr3t@example.com/x')": "s3cr3t",
            "token ghp_abcdefghijklmnopqrstuvwxyz0123456789 leaked": "ghp_abcdefghij",
            "X-Api-Key: key-1234567890": "key-1234567890",
            "cookie: session_id=abc123; tz=UTC": "abc123",
            "raised with the configured test-token inside": "test-token",
        }
        for text, secret in cases.items():
            with self.subTest(text=text):
                masked = company_id._sanitize_report_text(text)
                self.assertNotIn(secret, masked)
                self.assertIn(MASK, masked)
        self.assertEqual(
            company_id._sanitize_report_text("Record token_id=5 not found"),
            "Record token_id=5 not found",
        )

    def test_portal_user_cannot_send(self):
        portal_user = new_test_user(
            self.env, login="portal_ias", groups="base.group_portal"
        )
        with patch(REQUESTS_POST) as mock_post, self.assertRaises(AccessError):
            self.env["res.company"].with_user(portal_user).action_send_github_issue(
                name="Click here", traceback="Traceback"
            )
        mock_post.assert_not_called()

    def test_connection_test_needs_write_access(self):
        user = new_test_user(self.env, login="employee_ias", groups="base.group_user")
        with patch(REQUESTS_GET) as mock_get, self.assertRaises(AccessError):
            self.company_id.with_user(user).action_test_github_connection()
        mock_get.assert_not_called()

    def _module_traceback(self):
        module_file = f"{get_module_path('issue_auto_send')}/models/res_company.py"
        base_file = f"{get_module_path('base')}/models/ir_actions.py"
        return (
            "Traceback (most recent call last):\n"
            '  File "/opt/odoo/odoo/http.py", line 2599, in dispatch\n'
            f'  File "{base_file}", line 1016, in _run_action_code_multi\n'
            '  File "ir.actions.server(1,)", line 1, in <module>\n'
            f'  File "{module_file}", line 72, in action_raise_dummy_server_error\n'
            "AttributeError: 'unknown' object has no attribute 'id'\n\n"
            "The above server error caused the following client error:\n"
            "    at makeErrorFromResponse "
            "(http://localhost:19069/web/assets/web.assets_web.min.js:3195:165)"
        )

    def test_get_error_module(self):
        company_model = self.env["res.company"]
        self.assertEqual(
            company_model._get_error_module(self._module_traceback()), "issue_auto_send"
        )
        base_file = f"{get_module_path('base')}/models/ir_actions.py"
        self.assertEqual(
            company_model._get_error_module(f'File "{base_file}", line 1, in run'),
            "base",
        )
        self.assertEqual(
            company_model._get_error_module(
                'File "/opt/odoo/odoo/http.py", line 1, in x'
            ),
            "unknown",
        )
        self.assertEqual(company_model._get_error_module(""), "unknown")

    def test_get_error_module_chained_traceback(self):
        """safe_eval re-raises the error from base; the root cause wins."""
        module_file = f"{get_module_path('issue_auto_send')}/models/res_company.py"
        base_file = f"{get_module_path('base')}/models/ir_actions.py"
        traceback = (
            "Traceback (most recent call last):\n"
            '  File "<string>", line 1, in <module>\n'
            f'  File "{module_file}", line 90, in action_raise_dummy_server_error\n'
            "AttributeError: 'unknown' object has no attribute 'id'\n\n"
            "During handling of the above exception, another exception occurred:\n\n"
            "Traceback (most recent call last):\n"
            f'  File "{base_file}", line 1016, in _run_action_code_multi\n'
            '  File "/opt/odoo/odoo/tools/safe_eval.py", line 414, in safe_eval\n'
            "ValueError: AttributeError(...) while evaluating\n"
        )
        self.assertEqual(
            self.env["res.company"]._get_error_module(traceback), "issue_auto_send"
        )

    def test_error_digest_ignores_client_part_and_addresses(self):
        company_model = self.env["res.company"]
        server_part = "Traceback\nValueError: <object at 0x7f3a2b>"
        digest = company_model._get_error_digest(
            server_part
            + "\nThe above server error caused the following client error:\n"
            "at web.assets_web.min.js:1:1"
        )
        other_bundle = company_model._get_error_digest(
            "Traceback\nValueError: <object at 0x9999aa>\n"
            "The above server error caused the following client error:\n"
            "at web.assets_web.min.js:2:2"
        )
        self.assertEqual(digest, other_bundle)
        self.assertNotEqual(digest, company_model._get_error_digest("Other error"))

    def test_send_issue_title_contains_module(self):
        with patch(REQUESTS_POST, return_value=self._issue_response(3)) as mock_post:
            result = self._send(traceback=self._module_traceback())
        self.assertEqual(result["module"], "issue_auto_send")
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["title"], "[issue_auto_send] Odoo Server Error")
        self.assertIn("| Module | issue_auto_send |", payload["body"])

    def test_send_file(self):
        self.company_id.issue_auto_send_target = "file"
        file_url = (
            "https://github.com/weinni2000/error_logs_test/blob/main/odoo_errors/x.md"
        )
        response = MagicMock(status_code=201)
        response.json.return_value = {"content": {"html_url": file_url}}
        with (
            patch(REQUESTS_PUT, return_value=response) as mock_put,
            patch(REQUESTS_POST) as mock_post,
        ):
            result = self._send(traceback=self._module_traceback())
            self._send(traceback=self._module_traceback())
            second_url = mock_put.call_args.args[0]
        mock_post.assert_not_called()
        self.assertTrue(result["ok"])
        self.assertEqual(result["target"], "file")
        self.assertEqual(result["url"], file_url)
        url = mock_put.call_args_list[0].args[0]
        self.assertRegex(
            url,
            r"^https://api\.github\.com/repos/weinni2000/error_logs_test/contents/"
            r"odoo_errors/issue_auto_send/\d{4}-\d{2}-\d{2}/\d{6}_[0-9a-f]{8}\.md$",
        )
        # The second occurrence of the same error gets its own file.
        self.assertTrue(second_url.endswith("_2.md"), second_url)
        payload = mock_put.call_args_list[0].kwargs["json"]
        self.assertEqual(payload["message"], "[issue_auto_send] Odoo Server Error")
        content = base64.b64decode(payload["content"]).decode()
        self.assertTrue(content.startswith("# [issue_auto_send] Odoo Server Error"))
        self.assertIn("action_raise_dummy_server_error", content)

    def test_duplicates_skipped_within_period(self):
        self.company_id.write(
            {
                "issue_auto_send_skip_duplicates": True,
                "issue_auto_send_duplicate_hours": 24,
            }
        )
        with patch(REQUESTS_POST, return_value=self._issue_response(7)) as mock_post:
            first = self._send(traceback=self._module_traceback())
            second = self._send(traceback=self._module_traceback(), automatic=False)
            other = self._send(traceback="Traceback\nKeyError: 'x'")
        self.assertTrue(first["ok"])
        self.assertTrue(second["ok"])
        self.assertTrue(second["duplicate"])
        self.assertEqual(
            second["url"], "https://github.com/weinni2000/error_logs_test/issues/7"
        )
        self.assertTrue(other["ok"])
        self.assertNotIn("duplicate", other)
        self.assertEqual(mock_post.call_count, 2)
        log = self.env["issue.auto.send.log"].search(
            [
                (
                    "digest",
                    "=",
                    self.env["res.company"]._get_error_digest(self._module_traceback()),
                )
            ]
        )
        self.assertEqual(log.occurrence_count, 2)
        self.assertEqual(log.module, "issue_auto_send")

    def test_duplicates_sent_again_after_period(self):
        self.company_id.write(
            {
                "issue_auto_send_skip_duplicates": True,
                "issue_auto_send_duplicate_hours": 24,
            }
        )
        with patch(REQUESTS_POST, return_value=self._issue_response(8)) as mock_post:
            self._send(traceback=self._module_traceback())
            log = self.env["issue.auto.send.log"].search([], limit=1)
            log.last_sent_date = fields.Datetime.now() - timedelta(hours=25)
            result = self._send(traceback=self._module_traceback())
        self.assertNotIn("duplicate", result)
        self.assertEqual(mock_post.call_count, 2)

    def test_duplicates_once_forever(self):
        self.company_id.write(
            {
                "issue_auto_send_skip_duplicates": True,
                "issue_auto_send_duplicate_hours": 0,
            }
        )
        with patch(REQUESTS_POST, return_value=self._issue_response(9)) as mock_post:
            self._send(traceback=self._module_traceback())
            log = self.env["issue.auto.send.log"].search([], limit=1)
            log.last_sent_date = fields.Datetime.now() - timedelta(days=365)
            result = self._send(traceback=self._module_traceback())
        self.assertTrue(result["duplicate"])
        self.assertEqual(mock_post.call_count, 1)

    def test_duplicates_not_skipped_when_disabled(self):
        with patch(REQUESTS_POST, return_value=self._issue_response(10)) as mock_post:
            self._send(traceback=self._module_traceback())
            self._send(traceback=self._module_traceback())
        self.assertEqual(mock_post.call_count, 2)

    @mute_logger(MODEL_LOGGER)
    def test_failed_send_is_retried(self):
        self.company_id.issue_auto_send_skip_duplicates = True
        with patch(REQUESTS_POST, return_value=MagicMock(status_code=500, text="boom")):
            failed = self._send(traceback=self._module_traceback())
        with patch(REQUESTS_POST, return_value=self._issue_response(11)) as mock_post:
            retried = self._send(traceback=self._module_traceback())
        self.assertFalse(failed["ok"])
        self.assertTrue(retried["ok"])
        self.assertNotIn("duplicate", retried)
        mock_post.assert_called_once()

    def _enable_email(self):
        self.company_id.write(
            {
                "email": "odoo@example.com",
                "issue_auto_send_email_enabled": True,
                "issue_auto_send_email_to": "dev@example.com, ops@example.com",
            }
        )

    def test_send_email_with_same_content(self):
        self._enable_email()
        mail_server_class = type(self.env["ir.mail_server"])
        with (
            patch(REQUESTS_POST, return_value=self._issue_response(4)) as mock_post,
            patch.object(
                mail_server_class, "send_email", return_value="<msg-id>"
            ) as mock_send,
        ):
            result = self._send(
                message="password=super-secret", traceback=self._module_traceback()
            )
        self.assertTrue(result["ok"])
        self.assertTrue(result["github"]["ok"])
        self.assertEqual(
            result["email"],
            {"ok": True, "email_to": ["dev@example.com", "ops@example.com"]},
        )
        email_message = mock_send.call_args.args[0]
        issue = mock_post.call_args.kwargs["json"]
        self.assertEqual(email_message["Subject"], issue["title"])
        self.assertEqual(email_message["To"], "dev@example.com, ops@example.com")
        email_body = email_message.get_payload(decode=True).decode()
        self.assertEqual(
            email_body.strip(), f"# {issue['title']}\n\n{issue['body']}".strip()
        )
        self.assertNotIn("super-secret", email_body)

    def test_send_email_only(self):
        self._enable_email()
        self.company_id.issue_auto_send_github_url = False
        mail_server_class = type(self.env["ir.mail_server"])
        with (
            patch(REQUESTS_POST) as mock_post,
            patch.object(mail_server_class, "send_email", return_value="<msg-id>"),
        ):
            result = self._send(traceback=self._module_traceback())
        mock_post.assert_not_called()
        self.assertTrue(result["ok"])
        self.assertIsNone(result["github"])

    @mute_logger(MODEL_LOGGER)
    def test_send_email_failure_keeps_github_result(self):
        self._enable_email()
        mail_server_class = type(self.env["ir.mail_server"])
        with (
            patch(REQUESTS_POST, return_value=self._issue_response(5)),
            patch.object(
                mail_server_class,
                "send_email",
                side_effect=ConnectionRefusedError("no smtp"),
            ),
        ):
            result = self._send()
        self.assertTrue(result["ok"])
        self.assertEqual(result["email"], {"ok": False, "reason": "email_failed"})

    def test_send_not_configured(self):
        self.company_id.issue_auto_send_github_url = False
        result = self._send()
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "not_configured")

    @mute_logger(MODEL_LOGGER)
    def test_send_github_error(self):
        self.company_id.issue_auto_send_enabled = True
        with patch(
            REQUESTS_POST, return_value=MagicMock(status_code=404, text="Not Found")
        ):
            result = self._send()
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], 404)

    def _test_connection(
        self, get_status, post_status=None, put_status=None, private=True
    ):
        get_response = MagicMock(status_code=get_status)
        get_response.json.return_value = {"has_issues": True, "private": private}
        with (
            patch(REQUESTS_GET, return_value=get_response),
            patch(
                REQUESTS_POST, return_value=MagicMock(status_code=post_status)
            ) as mock_post,
            patch(
                REQUESTS_PUT, return_value=MagicMock(status_code=put_status)
            ) as mock_put,
        ):
            check = self.company_id._check_github_connection()
        return check, mock_post if put_status is None else mock_put

    def test_connection_file_writable(self):
        self.company_id.issue_auto_send_target = "file"
        check, mock_put = self._test_connection(200, put_status=422)
        self.assertTrue(check["ok"], check["message"])
        self.assertIn("files can be created", check["message"])
        self.assertTrue(
            mock_put.call_args.args[0].endswith(
                "/contents/odoo_errors/.connection_test"
            )
        )

    def test_connection_file_read_only(self):
        self.company_id.issue_auto_send_target = "file"
        check, _mock_put = self._test_connection(200, put_status=403)
        self.assertFalse(check["ok"])
        self.assertIn("Contents: Read and write", check["message"])

    def test_connection_writable(self):
        check, mock_post = self._test_connection(200, 422)
        self.assertTrue(check["ok"], check["message"])
        self.assertFalse(check["public"])
        self.assertEqual(mock_post.call_args.kwargs["json"], {})

    def test_connection_public_repository_warns(self):
        check, _mock_post = self._test_connection(200, 422, private=False)
        self.assertTrue(check["ok"])
        self.assertTrue(check["public"])
        self.assertIn("public", check["message"])

    def test_connection_read_only(self):
        check, _mock_post = self._test_connection(200, 403)
        self.assertFalse(check["ok"])
        self.assertIn("may not create issues", check["message"])

    def test_connection_repo_not_found(self):
        check, mock_post = self._test_connection(404)
        self.assertFalse(check["ok"])
        self.assertIn("not found", check["message"])
        mock_post.assert_not_called()

    def test_action_test_github_connection_stores_result(self):
        with patch(REQUESTS_GET, return_value=MagicMock(status_code=401)):
            action = self.company_id.action_test_github_connection()
        self.assertEqual(action["params"]["type"], "danger")
        self.assertIn(
            "rejected the token", self.company_id.issue_auto_send_check_result
        )

    def test_raise_dummy_server_error(self):
        with self.assertRaises(AttributeError):
            self.env["res.company"].action_raise_dummy_server_error()
