from odoo import api, fields, models


class EncryptedAuditLog(models.Model):
    """Audit log for encrypted field access."""

    _name = "pb.encrypted.audit.log"
    _description = "Encrypted Field Audit Log"
    _order = "create_date desc"
    _rec_name = "display_name"

    user_id = fields.Many2one(
        "res.users",
        required=True,
        index=True,
        readonly=True,
    )
    model_name = fields.Char(
        required=True,
        index=True,
        readonly=True,
    )
    field_name = fields.Char(
        required=True,
        index=True,
        readonly=True,
    )
    record_id = fields.Integer(
        required=True,
        index=True,
        readonly=True,
    )
    action = fields.Selection(
        [
            ("decrypt", "Decrypted"),
            ("export", "Exported"),
        ],
        required=True,
        readonly=True,
        default="decrypt",
    )
    create_date = fields.Datetime(
        string="Access Time",
        readonly=True,
    )

    display_name = fields.Char(
        string="Description",
        compute="_compute_display_name",
        store=False,
    )

    @api.depends("user_id", "model_name", "field_name", "record_id")
    def _compute_display_name(self):
        for log in self:
            log.display_name = (
                f"{log.user_id.name} accessed "
                f"{log.model_name}.{log.field_name} (ID: {log.record_id})"
            )

    @api.model
    def cleanup_old_logs(self, days=None):
        """Delete audit logs older than specified days.

        If days is not specified, reads from system parameter
        'encryption.audit_log_retention_days' (default: 90).
        """
        from datetime import datetime, timedelta

        if days is None:
            days = int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("encryption.audit_log_retention_days", "90")
            )
        cutoff = datetime.now() - timedelta(days=days)
        old_logs = self.search([("create_date", "<", cutoff)])
        count = len(old_logs)
        old_logs.unlink()
        return count

    @api.model
    def get_access_report(
        self,
        model_name=None,
        field_name=None,
        user_id=None,
        date_from=None,
        date_to=None,
    ):
        """Generate access report for encrypted fields."""
        domain = []
        if model_name:
            domain.append(("model_name", "=", model_name))
        if field_name:
            domain.append(("field_name", "=", field_name))
        if user_id:
            domain.append(("user_id", "=", user_id))
        if date_from:
            domain.append(("create_date", ">=", date_from))
        if date_to:
            domain.append(("create_date", "<=", date_to))

        logs = self.search(domain, order="create_date desc")
        return logs
