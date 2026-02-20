# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import HttpCase, tagged

from .common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestAuditlogHttp(HttpCase, AuditLogRuleCommon):
    def test_compute_display_name(self):
        self.authenticate("admin", "admin")
        rule = self.env["auditlog.rule"].create(
            {
                "name": "res.partner",
                "model_id": self.env.ref("base.model_res_partner").id,
                "log_type": "full",
                "state": "subscribed",
            }
        )
        self.addCleanup(rule.unsubscribe)
        partner = self.env.ref("base.partner_demo")
        self.make_jsonrpc_request(
            "/web/dataset/call_kw",
            params={
                "model": "res.partner",
                "method": "write",
                "args": [partner.id, {"name": "test"}],
                "kwargs": {},
            },
            headers={
                "Cookie": f"session_id={self.session.sid};",
            },
        )
        logs = self.env["auditlog.log"].search(
            [("model_id", "=", rule.model_id.id), ("res_id", "=", partner.id)]
        )
        self.assertEqual(len(logs), 1)
        http_request_id = logs[0]["http_request_id"]
        self.assertRegex(
            http_request_id.display_name,
            r"/web/dataset/call_kw \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\)",
        )
        http_session_id = logs[0]["http_session_id"]
        self.assertRegex(
            http_session_id.display_name,
            r"Mitchell Admin \(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\)",
        )
