# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import tools

from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


class TestAuditlogStdout(AuditLogRuleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.groups_model_id = cls.env.ref("base.model_res_groups").id
        cls.groups_rule = cls.env["auditlog.rule"].create(
            {
                "name": "testrule for stdout",
                "model_id": cls.groups_model_id,
                "log_export_data": True,
                "stdout": True,
            }
        )
        cls.groups_rule.subscribe()

    def test_LogStdOut(self):
        """Test that the values of an auditlog are shown in the logger."""
        # logging is disabled when testing
        tools.config["test_enable"] = False

        auditlog_log = self.env["auditlog.log"]
        logger_name = "odoo.addons.auditlog_stdout.models.auditlog_log"
        with self.assertLogs(logger=logger_name) as capt:
            self.env["res.groups"].search([]).export_data(["name"])
            created_log = auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "export_data"),
                ]
            )
        self.assertFalse(created_log)
        self.assertIn('"method": "export_data"', capt.output[0])

    def test_LogStdOut_with_format_specified(self):
        """Test that the values of an auditlog are shown in the logger,
        using the provided format."""
        self.env["ir.config_parameter"].set_param(
            "auditlog.stdout_log_format_json",
            '{{"user": "{user_id}", "model": "{model_model}"}}',
        )
        # logging is disabled when testing
        tools.config["test_enable"] = False

        auditlog_log = self.env["auditlog.log"]
        logger_name = "odoo.addons.auditlog_stdout.models.auditlog_log"
        with self.assertLogs(logger=logger_name) as capt:
            self.env["res.groups"].search([]).export_data(["name"])
            created_log = auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "export_data"),
                ]
            )
        self.assertFalse(created_log)
        self.assertIn(
            '"user": "{uid}", "model": "{model_model}"'.format(
                uid=self.env.user.id,
                model_model=self.env.ref("base.model_res_groups").model,
            ),
            capt.output[0],
        )

    def test_LogStdOut_with_invalid_format_specified(self):
        """Test that the default values of an auditlog are shown in the logger,
        when an invalid format has been specified."""
        self.env["ir.config_parameter"].set_param(
            "auditlog.stdout_log_format_json",
            "INVALID",
        )
        # logging is disabled when testing
        tools.config["test_enable"] = False

        auditlog_log = self.env["auditlog.log"]
        logger_name = "odoo.addons.auditlog_stdout.models.auditlog_log"
        with self.assertLogs(logger=logger_name) as capt:
            self.env["res.groups"].search([]).export_data(["name"])
            created_log = auditlog_log.search(
                [
                    ("model_id", "=", self.groups_model_id),
                    ("method", "=", "export_data"),
                ]
            )
        self.assertFalse(created_log)
        self.assertIn('"method": "export_data"', capt.output[0])
        self.assertIn(
            "auditlogging to standard output failed",
            capt.output[1],
        )
