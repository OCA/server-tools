from odoo.tests import tagged

from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestWebRead(AuditLogRuleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test partner"})
        cls.rule = cls.create_rule(
            {
                "name": __name__,
                "model_id": cls.env.ref("base.model_res_partner").id,
                "log_read": True,
                "log_create": False,
                "log_write": False,
                "log_unlink": False,
                "log_type": "full",
            }
        )
        cls.rule.subscribe()

    def _search_read_logs(self):
        return self.env["auditlog.log"].search(
            [
                ("model_id", "=", self.rule.model_id.id),
                ("method", "=", "read"),
                ("res_id", "=", self.partner.id),
            ]
        )

    def test_web_read(self):
        """web_read goes through read, so it is logged once"""
        self.partner.web_read({"name": {}, "email": {}})
        log = self._search_read_logs().ensure_one()
        self.assertEqual(set(log.line_ids.mapped("field_name")), {"name", "email"})

    def test_web_search_read(self):
        """web_search_read goes through read, so it is logged once"""
        self.env["res.partner"].web_search_read(
            [("id", "=", self.partner.id)], {"name": {}}
        )
        log = self._search_read_logs().ensure_one()
        self.assertEqual(log.line_ids.mapped("field_name"), ["name"])
