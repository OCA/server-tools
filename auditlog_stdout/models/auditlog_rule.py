# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    stdout = fields.Boolean(
        string="Output to STDOUT",
        help="If set, the log entries will be only logged to STDOUT "
        "(rather than creating an auditlog log and line entries).",
    )

    def create_logs(
        self,
        uid,
        res_model,
        res_ids,
        method,
        old_values=None,
        new_values=None,
        additional_log_values=None,
    ):
        """Pass the auditlog_use_stdout in the context,
        later caught in the create of the log entries,
        to output the values to STDOUT instead of creating a log entry.
        """
        model_id = self.pool._auditlog_model_cache[res_model]
        auditlog_rule = self.env["auditlog.rule"].search([("model_id", "=", model_id)])
        if auditlog_rule.stdout:
            self = self.with_context(auditlog_use_stdout=True)
        return super().create_logs(
            uid,
            res_model,
            res_ids,
            method,
            old_values=old_values,
            new_values=new_values,
            additional_log_values=additional_log_values,
        )
