import base64
import hashlib
import json
import logging
import re
from datetime import timedelta

import requests

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.http import request as http_request
from odoo.modules.module import get_resource_from_path

_logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com"
GITHUB_REPO_URL_RE = re.compile(
    r"github\.com[/:](?P<owner>[\w.-]+)/(?P<repo>[\w.-]+?)(?:\.git)?/?$"
)
GITHUB_TIMEOUT = 15
# Standardized location of error reports sent as files; the module is taken from
# the traceback.
GITHUB_FILE_PATH = "odoo_errors/{module}/{date}/{time}_{digest}{suffix}.md"
GITHUB_FILE_PROBE_PATH = "odoo_errors/.connection_test"
TRACEBACK_HEADER = "Traceback (most recent call last):"
TRACEBACK_FILE_RE = re.compile(r'File "(?P<path>[^"]+)", line \d+')
# The client part of a traceback contains asset URLs that change with every
# bundle, so it is left out of the duplicate detection.
CLIENT_ERROR_SEPARATOR = "The above server error caused the following client error"
HEX_ADDRESS_RE = re.compile(r"0x[0-9a-fA-F]+")
UNKNOWN_MODULE = "unknown"
SENSITIVE_KEYS = frozenset(
    {
        "access_token",
        "api_key",
        "apikey",
        "authorization",
        "client_secret",
        "cookie",
        "csrf_token",
        "passwd",
        "password",
        "private_key",
        "refresh_token",
        "secret",
        "sentry_dsn",
        "session_id",
        "token",
        "x-api-key",
    }
)
_SENSITIVE_KEYS_PATTERN = "|".join(
    re.escape(key) for key in sorted(SENSITIVE_KEYS, key=len, reverse=True)
)
# key=value, key: value, "key": "value" and 'key': 'value', including an
# optional authorization scheme ("Authorization: Bearer <token>").
SENSITIVE_KEYVAL_RE = re.compile(
    r"(?P<prefix>(?<![\w-])[\"']?(?:" + _SENSITIVE_KEYS_PATTERN + r")[\"']?"
    r"\s*[:=]\s*[\"']?)"
    r"(?P<value>(?:(?:Bearer|Basic|Token)\s+)?[^\s\"'&;,}\]]+)",
    re.IGNORECASE,
)
AUTH_SCHEME_RE = re.compile(
    r"\b(?P<scheme>Bearer|Basic)\s+[A-Za-z0-9._~+/=-]{8,}", re.IGNORECASE
)
URL_CREDENTIALS_RE = re.compile(
    r"(?P<prefix>\b[a-z][a-z0-9+.-]*://[^/\s:@]+:)[^@\s/]+@", re.IGNORECASE
)
GITHUB_TOKEN_RE = re.compile(
    r"\b(?:gh[opusr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
)
SENSITIVE_VALUE_RE = re.compile(r"^(?:\d[ -]*?){13,16}$")
MASK = "*" * 8


class ResCompany(models.Model):
    _inherit = "res.company"

    issue_auto_send_enabled = fields.Boolean(
        string="Send Server Errors Automatically",
        help="If enabled, server errors with a traceback are reported as soon as "
        "the error dialog opens. Otherwise they are only reported when the user "
        "clicks the send button in the error dialog.",
    )
    issue_auto_send_github_url = fields.Char(
        string="GitHub Repository URL",
        help="GitHub repository where error reports are created, for example "
        "https://github.com/my-company/odoo-errors. Use a private repository: "
        "reports contain user logins, IP addresses and data from tracebacks.",
    )
    issue_auto_send_github_user = fields.Char(
        string="GitHub User",
        help="GitHub account used to create the reports. It must have access to "
        "the repository.",
    )
    issue_auto_send_github_token = fields.Char(
        string="GitHub Token",
        groups="base.group_system",
        help="Personal access token of the GitHub user with permission to create "
        "issues or files in the repository.",
    )
    issue_auto_send_target = fields.Selection(
        selection=[("issue", "Issue"), ("file", "File in Repository")],
        string="Send As",
        default="issue",
        required=True,
        help="Issue: create a GitHub issue per error.\n"
        "File in Repository: commit a Markdown file per error to "
        "odoo_errors/<module>/<YYYY-MM-DD>/<HHMMSS>_<hash>.md, where <module> is "
        "the Odoo module that raised the error and <hash> identifies the "
        "traceback.",
    )
    issue_auto_send_email_enabled = fields.Boolean(
        string="Send by Email",
        help="Also send the error report (same subject and content as on GitHub) "
        "by email through the outgoing mail server.",
    )
    issue_auto_send_email_to = fields.Char(
        string="Email Recipients",
        help="Comma-separated email addresses that receive the error reports.",
    )
    issue_auto_send_skip_duplicates = fields.Boolean(
        string="Skip Duplicate Errors",
        default=False,
        help="Do not report an error again when the same traceback was already "
        "reported within the duplicate period. Occurrences are still counted in "
        "the error report log.",
    )
    issue_auto_send_duplicate_hours = fields.Integer(
        string="Duplicate Period (Hours)",
        default=24,
        help="An error with the same traceback is reported again once this many "
        "hours have passed since it was last reported. 0 reports each error only "
        "once.",
    )
    issue_auto_send_check_result = fields.Text(
        string="Last Connection Test",
        readonly=True,
        copy=False,
    )
    issue_auto_send_show_advanced = fields.Boolean(
        string="Advanced Options",
        store=False,
        help="Show the advanced error report settings.",
    )

    @api.model
    def action_raise_dummy_server_error(self):
        """Raise a real server error so the send button can be tested."""
        raise AttributeError("'unknown' object has no attribute 'id'")

    @api.model
    def action_send_github_issue(
        self, name="", message="", traceback="", context_details="", automatic=False
    ):
        """Report an error from the web client error dialog.

        Callable over RPC, so the report is only accepted from internal users:
        it runs with the company's GitHub token and outgoing mail server.
        """
        if not self.env.user._is_internal():
            raise AccessError(self.env._("Only internal users can send error reports."))
        return self.env.company.sudo()._send_error_report(
            name=name,
            message=message,
            traceback=traceback,
            context_details=context_details,
            automatic=automatic,
        )

    def action_test_github_connection(self):
        """Check that GitHub is reachable and the token may create reports,
        without creating one."""
        self.ensure_one()
        # Uses the token and stores the result: only for users allowed to edit
        # the company.
        self.check_access("write")
        company_id = self.sudo()
        check = company_id._check_github_connection()
        company_id.issue_auto_send_check_result = (
            f"{fields.Datetime.now()} UTC: {check['message']}"
        )
        if not check["ok"]:
            notification_type = "danger"
        elif check.get("public"):
            notification_type = "warning"
        else:
            notification_type = "success"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": self.env._("GitHub Connection Test"),
                "message": check["message"],
                "type": notification_type,
                "sticky": notification_type != "success",
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }

    def _check_github_connection(self):
        """Return ``{"ok": bool, "message": str, "public": bool}``.

        Write access is probed by sending an invalid create request (an issue
        without a title, or a file without content): GitHub checks permissions
        first, so 422 (validation error) means the token may write, while 403/404
        mean it may not. Nothing is created.
        """
        self.ensure_one()
        repo_path = self._get_github_repo_path()
        if not repo_path:
            return {
                "ok": False,
                "message": self.env._("The GitHub Repository URL is invalid."),
            }
        if not self.issue_auto_send_github_token:
            return {
                "ok": False,
                "message": self.env._("No GitHub token is configured."),
            }
        repo_url = f"{GITHUB_API_URL}/repos/{repo_path}"
        is_file = self.issue_auto_send_target == "file"
        try:
            response = requests.get(
                repo_url, headers=self._get_github_headers(), timeout=GITHUB_TIMEOUT
            )
            if response.status_code == 401:
                message = self.env._("GitHub rejected the token (invalid or expired).")
                return {"ok": False, "message": message}
            if response.status_code == 404:
                message = self.env._(
                    "Repository %(repo)s not found. Either it does not exist or "
                    "the token has no access to it (fine-grained tokens must list "
                    "the repository under 'Repository access')."
                )
                return {"ok": False, "message": message % {"repo": repo_path}}
            if response.status_code != 200:
                message = self.env._("GitHub answered HTTP %(status)s: %(text)s")
                return {
                    "ok": False,
                    "message": message
                    % {"status": response.status_code, "text": response.text[:300]},
                }
            repo_info = response.json()
            is_public = repo_info.get("private") is False
            if not is_file and not repo_info.get("has_issues", True):
                message = self.env._("Issues are disabled in repository %(repo)s.")
                return {"ok": False, "message": message % {"repo": repo_path}}
            if is_file:
                response = requests.put(
                    f"{repo_url}/contents/{GITHUB_FILE_PROBE_PATH}",
                    json={},
                    headers=self._get_github_headers(),
                    timeout=GITHUB_TIMEOUT,
                )
            else:
                response = requests.post(
                    f"{repo_url}/issues",
                    json={},
                    headers=self._get_github_headers(),
                    timeout=GITHUB_TIMEOUT,
                )
        except requests.RequestException as error:
            message = self.env._("GitHub is not reachable: %(error)s")
            return {"ok": False, "message": message % {"error": error}}
        if response.status_code == 422:
            if is_file:
                message = self.env._(
                    "GitHub is reachable and files can be created in %(repo)s."
                )
            else:
                message = self.env._(
                    "GitHub is reachable and issues can be created in %(repo)s."
                )
            message = message % {"repo": repo_path}
            if is_public:
                warning = self.env._(
                    "Warning: the repository is public, so error reports (user "
                    "logins, IP addresses, data from tracebacks) are visible to "
                    "everyone. Use a private repository."
                )
                message = f"{message}\n{warning}"
            return {"ok": True, "message": message, "public": is_public}
        if response.status_code in (403, 404):
            if is_file:
                message = self.env._(
                    "Repository %(repo)s is readable, but the token may not create "
                    "files (fine-grained tokens need 'Contents: Read and write')."
                )
            else:
                message = self.env._(
                    "Repository %(repo)s is readable, but the token may not create "
                    "issues (fine-grained tokens need 'Issues: Read and write')."
                )
            return {"ok": False, "message": message % {"repo": repo_path}}
        message = self.env._("GitHub answered HTTP %(status)s: %(text)s")
        return {
            "ok": False,
            "message": message
            % {"status": response.status_code, "text": response.text[:300]},
        }

    def _get_github_headers(self):
        self.ensure_one()
        return {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.issue_auto_send_github_token}",
            "User-Agent": self.issue_auto_send_github_user or "odoo-issue-auto-send",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _get_github_repo_path(self):
        self.ensure_one()
        match = GITHUB_REPO_URL_RE.search(
            (self.issue_auto_send_github_url or "").strip()
        )
        if not match:
            return False
        return f"{match['owner']}/{match['repo']}"

    @api.model
    def _get_error_module(self, traceback):
        """Return the Odoo module of the innermost traceback frame of an addon.

        Chained tracebacks ("During handling of the above exception ...") are
        searched from the root cause on, because wrappers such as ``safe_eval``
        re-raise the original error from core code. Frames of the Odoo core
        (``odoo/http.py``, ``odoo/orm/...``) and JavaScript frames are not inside
        an addons path and are skipped.
        """
        for block in (traceback or "").split(TRACEBACK_HEADER):
            for path in reversed(TRACEBACK_FILE_RE.findall(block)):
                resource = get_resource_from_path(path)
                if resource and re.fullmatch(r"\w+", resource[0]):
                    return resource[0]
        return UNKNOWN_MODULE

    @api.model
    def _get_error_digest(self, traceback, title=""):
        """Return a short hash identifying an error, stable across occurrences.

        Only the server part of the traceback is used, without memory
        addresses, so the same error gets the same digest every time.
        """
        text = (traceback or title or "").split(CLIENT_ERROR_SEPARATOR)[0]
        text = HEX_ADDRESS_RE.sub("0x", text).strip()
        return hashlib.sha1(text.encode()).hexdigest()[:8]

    def _sanitize_report_text(self, value):
        if not isinstance(value, str):
            return value
        if SENSITIVE_VALUE_RE.match(value):
            return MASK
        token = self.issue_auto_send_github_token
        if token and token in value:
            value = value.replace(token, MASK)
        value = SENSITIVE_KEYVAL_RE.sub(r"\g<prefix>" + MASK, value)
        value = AUTH_SCHEME_RE.sub(r"\g<scheme> " + MASK, value)
        value = URL_CREDENTIALS_RE.sub(r"\g<prefix>" + MASK + "@", value)
        return GITHUB_TOKEN_RE.sub(MASK, value)

    def _sanitize_report_value(self, key, value):
        if isinstance(key, str) and any(
            sensitive_key in key.lower() for sensitive_key in SENSITIVE_KEYS
        ):
            return MASK
        if isinstance(value, dict):
            return {
                item_key: self._sanitize_report_value(item_key, item_value)
                for item_key, item_value in value.items()
            }
        if isinstance(value, list | tuple):
            return [
                self._sanitize_report_value(key, item_value) for item_value in value
            ]
        return self._sanitize_report_text(value)

    def _get_current_request_context(self):
        try:
            request_obj = http_request
            session = getattr(request_obj, "session", {})
            httprequest = getattr(request_obj, "httprequest", None)
        except RuntimeError:
            return {}
        request_context = {
            "tags": {
                "database": session.get("db"),
            },
            "user": {
                "id": session.get("uid"),
                "login": session.get("login"),
            },
            "extra": {
                "context": session.get("context", {}),
            },
        }
        if httprequest:
            request_context["request"] = {
                "url": httprequest.base_url,
                "query_string": httprequest.query_string.decode("utf-8", "replace"),
                "method": httprequest.method,
                "remote_addr": httprequest.environ.get("REMOTE_ADDR"),
            }
        return request_context

    def _prepare_github_issue_report(
        self, name, message, traceback, context_details, automatic=False
    ):
        self.ensure_one()
        request_context = self._get_current_request_context()
        report = {
            "title": name or "Odoo Server Error",
            "message": message,
            "traceback": traceback,
            "context_details": context_details,
            "tags": {
                "database": self.env.cr.dbname,
                "company": self.name,
                "module": self._get_error_module(traceback),
                "automatic": automatic,
            },
        }
        report["tags"].update(request_context.pop("tags", {}))
        report.update(request_context)
        return self._sanitize_report_value(None, report)

    def _format_github_code_block(self, value, language=""):
        escaped_value = str(value or "").replace("```", "'''")
        return f"```{language}\n{escaped_value}\n```"

    def _format_github_json_block(self, value):
        return self._format_github_code_block(
            json.dumps(value, indent=2, sort_keys=True, default=str),
            "json",
        )

    def _prepare_github_issue_body(self, report):
        self.ensure_one()
        tags = report.get("tags", {})
        user = report.get("user", {})
        request_info = report.get("request", {})
        environment_rows = [
            ("Module", tags.get("module")),
            ("Database", tags.get("database")),
            ("Company", tags.get("company")),
            ("Automatic", tags.get("automatic")),
            ("User", user.get("login") or user.get("id")),
            ("URL", request_info.get("url")),
            ("Method", request_info.get("method")),
            ("Remote Address", request_info.get("remote_addr")),
        ]
        rows = "\n".join(
            f"| {label} | {value} |"
            for label, value in environment_rows
            if value not in (None, "")
        )
        parts = [
            f"Reported by Odoo database `{tags.get('database')}`, "
            f"company `{tags.get('company')}`.",
            f"### Environment\n\n| Key | Value |\n| --- | --- |\n{rows}",
        ]
        if report.get("message"):
            parts.append(f"### Message\n\n{report['message']}")
        if report.get("context_details"):
            context_block = self._format_github_code_block(report["context_details"])
            parts.append(f"### Context\n\n{context_block}")
        structured_context = {
            key: report[key]
            for key in ("tags", "user", "request", "extra")
            if report.get(key)
        }
        if structured_context:
            json_block = self._format_github_json_block(structured_context)
            parts.append(f"### Structured Context\n\n{json_block}")
        if report.get("traceback"):
            traceback_block = self._format_github_code_block(
                report["traceback"], "python"
            )
            parts.append(f"### Traceback\n\n{traceback_block}")
        return "\n\n".join(parts)

    def _get_github_file_path(self, report, digest, occurrence=1):
        now = fields.Datetime.now()
        return GITHUB_FILE_PATH.format(
            module=report["tags"]["module"],
            date=now.strftime("%Y-%m-%d"),
            time=now.strftime("%H%M%S"),
            digest=digest,
            # Two occurrences of the same error within one second would
            # otherwise target the same file, which GitHub refuses.
            suffix=f"_{occurrence}" if occurrence > 1 else "",
        )

    def _get_error_report_log(self, digest):
        self.ensure_one()
        return (
            self.env["issue.auto.send.log"]
            .sudo()
            .search(
                [("company_id", "=", self.id), ("digest", "=", digest)],
                order="last_date desc, id desc",
                limit=1,
            )
        )

    def _is_duplicate_error(self, log):
        """Whether an error already logged in ``log`` must not be reported again."""
        self.ensure_one()
        if not self.issue_auto_send_skip_duplicates or not log.last_sent_date:
            return False
        if self.issue_auto_send_duplicate_hours <= 0:
            return True
        period = timedelta(hours=self.issue_auto_send_duplicate_hours)
        return log.last_sent_date > fields.Datetime.now() - period

    def _send_error_report(
        self, name, message, traceback, context_details, automatic=False
    ):
        """Send the error report to GitHub (issue or file) and/or by email."""
        self.ensure_one()
        if automatic and not self.issue_auto_send_enabled:
            return {"ok": False, "reason": "disabled"}
        send_github = bool(self.issue_auto_send_github_url)
        send_email = bool(
            self.issue_auto_send_email_enabled and self.issue_auto_send_email_to
        )
        if not send_github and not send_email:
            return {"ok": False, "reason": "not_configured"}

        report = self._prepare_github_issue_report(
            name, message, traceback, context_details, automatic=automatic
        )
        module = report["tags"]["module"]
        title = f"[{module}] {report['title']}"
        digest = self._get_error_digest(traceback, report["title"])
        log = self._get_error_report_log(digest)
        now = fields.Datetime.now()
        if log and self._is_duplicate_error(log):
            log.write({"occurrence_count": log.occurrence_count + 1, "last_date": now})
            return {
                "ok": True,
                "duplicate": True,
                "module": module,
                "title": title,
                "url": log.url,
                "occurrence_count": log.occurrence_count,
            }

        occurrence = log.occurrence_count + 1 if log else 1
        body = self._prepare_github_issue_body(report)
        result = {"module": module, "title": title, "github": None, "email": None}
        if send_github:
            result["github"] = self._send_github_report(
                report, title, body, digest, occurrence
            )
            # Keep the GitHub keys (url, reason, status, ...) at top level for the
            # client.
            result.update(result["github"])
        if send_email:
            result["email"] = self._send_error_report_email(title, body)
        result["ok"] = any(
            channel and channel["ok"] for channel in (result["github"], result["email"])
        )
        log_vals = {"occurrence_count": occurrence, "last_date": now}
        if result["ok"]:
            log_vals["last_sent_date"] = now
            if result["github"] and result["github"].get("url"):
                log_vals["url"] = result["github"]["url"]
        if log:
            log.write(log_vals)
        else:
            self.env["issue.auto.send.log"].sudo().create(
                {
                    **log_vals,
                    "company_id": self.id,
                    "digest": digest,
                    "module": module,
                    "title": title,
                    "first_date": now,
                }
            )
        return result

    def _send_error_report_email(self, title, body):
        """Send the report by email with the same subject and content as on
        GitHub."""
        self.ensure_one()
        mail_server_model = self.env["ir.mail_server"]
        email_from = (
            self.partner_id.email_formatted
            or mail_server_model._get_default_from_address()
        )
        if not email_from:
            return {"ok": False, "reason": "missing_email_from"}
        email_to = [
            email.strip()
            for email in self.issue_auto_send_email_to.split(",")
            if email.strip()
        ]
        try:
            email_message = mail_server_model._build_email__(
                email_from=email_from,
                email_to=email_to,
                subject=title,
                body=f"# {title}\n\n{body}\n",
                subtype="plain",
            )
            mail_server_model.send_email(email_message)
        # Never let the report mail raise a second error dialog.
        except Exception as error:  # noqa: BLE001
            _logger.warning(
                "Error report email to %(to)s failed: %(error)s",
                {"to": email_to, "error": error},
            )
            return {"ok": False, "reason": "email_failed"}
        _logger.info("Error report email sent to %(to)s", {"to": email_to})
        return {"ok": True, "email_to": email_to}

    def _send_github_report(self, report, title, body, digest, occurrence=1):
        """Create a GitHub issue or commit a file with the report in the configured
        repository."""
        self.ensure_one()
        repo_path = self._get_github_repo_path()
        if not repo_path:
            return {"ok": False, "reason": "invalid_url"}
        if not self.issue_auto_send_github_token:
            return {"ok": False, "reason": "missing_token"}

        target = self.issue_auto_send_target or "issue"
        try:
            if target == "file":
                file_path = self._get_github_file_path(report, digest, occurrence)
                content = base64.b64encode(f"# {title}\n\n{body}\n".encode()).decode()
                response = requests.put(
                    f"{GITHUB_API_URL}/repos/{repo_path}/contents/{file_path}",
                    json={"message": title, "content": content},
                    headers=self._get_github_headers(),
                    timeout=GITHUB_TIMEOUT,
                )
            else:
                response = requests.post(
                    f"{GITHUB_API_URL}/repos/{repo_path}/issues",
                    json={"title": title, "body": body},
                    headers=self._get_github_headers(),
                    timeout=GITHUB_TIMEOUT,
                )
        except requests.RequestException as error:
            _logger.warning(
                "GitHub %(target)s send to %(repo)s failed: %(error)s",
                {"target": target, "repo": repo_path, "error": error},
            )
            return {"ok": False, "reason": "request_failed"}

        if response.status_code != 201:
            _logger.warning(
                "GitHub %(target)s send to %(repo)s failed with status %(status)s: "
                "%(text)s",
                {
                    "target": target,
                    "repo": repo_path,
                    "status": response.status_code,
                    "text": response.text[:500],
                },
            )
            return {
                "ok": False,
                "reason": "github_error",
                "status": response.status_code,
            }

        data = response.json()
        if target == "file":
            url = data.get("content", {}).get("html_url")
        else:
            url = data.get("html_url")
        _logger.info(
            "GitHub %(target)s created: %(url)s", {"target": target, "url": url}
        )
        result = {
            "ok": True,
            "target": target,
            "github_url": self.issue_auto_send_github_url,
            "url": url,
        }
        if target == "issue":
            result["issue_url"] = url
        return result
