import base64
import logging

from pytz import timezone

import odoo
from odoo import Command, _, api, fields, models, tools
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare
from odoo.tools.safe_eval import safe_eval, test_python_expr

from odoo.addons.queue_job.job import identity_exact

_logger = logging.getLogger(__name__)


class BaseNotificationRule(models.Model):
    _name = "base.notification.rule"
    _description = "Generic Notification Rule"
    _rec_name = "name"

    DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment
#  - model: Odoo Model of the record; is a void recordset
#  - rule: base.notification.rule record; may be void
#  - record: record; may be void
#  - records: recordset of all records in multi-mode; may be void
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - float_compare: Odoo function to compare floats based on specific precisions
#  - log: log(message, level='info')
#  - UserError: Warning Exception to use with raise
#  - Command: x2Many commands namespace

# To return partners, assign: partners = env['res.partner'].browse(3)
# To return a message, assign: message = "foo"\n\n\n\n"""

    name = fields.Char(required=True)
    model_id = fields.Many2one(
        "ir.model",
        string="Model",
        required=True,
        ondelete="cascade",
    )
    model = fields.Char(
        related="model_id.model",
    )
    trigger = fields.Selection(
        [
            ("on_create", "On Create"),
            ("on_write", "On Write"),
            ("on_unlink", "On Delete"),
            ("on_method_call", "On Method Call"),
        ],
        required=True,
        default="on_write",
    )
    method_name = fields.Char()
    domain = fields.Char("Domain Filter", default="[]")
    active = fields.Boolean(default=True)
    notify_mode = fields.Selection(
        [
            ("immediate", "Immediate"),
            ("queued", "Queued"),
        ],
        required=True,
        default="immediate",
    )
    message_type = fields.Selection(
        [
            ("chatter_log", "Log message in chatter and send email"),
            ("email", "Send email"),
        ],
        required=True,
        default="email",
    )
    partner_ids = fields.Many2many("res.partner", string="Recipients")
    python_code = fields.Text(
        groups="base.group_system",
        default=DEFAULT_PYTHON_CODE,
        help="Custom code to generate a message and recipients.\n"
        "Available variables: env, model, records, message, partners",
    )

    @api.constrains("python_code")
    def _check_python_code(self):
        for action in self.sudo().filtered("python_code"):
            msg = test_python_expr(expr=action.python_code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def _get_notification_message(self, records):
        self.ensure_one()
        record_ids_str = ", ".join(map(str, records.ids))
        message = _(
            "Event: %(trigger)s for model: %(model)s (IDs: %(ids)s) was triggered"
        ) % {
            "trigger": self.trigger,
            "model": records._description,
            "ids": record_ids_str,
        }
        return message

    def _get_dynamic_message_and_partners(self, records):
        """Safely execute user-defined Python code to compute message and recipients."""
        self.ensure_one()
        message = self._get_notification_message(records)
        partners = self.partner_ids

        def log(message, level="info"):
            self.env["ir.logging"].sudo().create(
                {
                    "type": "server",
                    "dbname": self._cr.dbname,
                    "name": __name__,
                    "level": level,
                    "message": message,
                    "path": "action",
                    "line": self.id,
                    "func": self.name,
                }
            )

        localdict = {
            "uid": self._uid,
            "user": self.env.user,
            "time": tools.safe_eval.time,
            "datetime": tools.safe_eval.datetime,
            "dateutil": tools.safe_eval.dateutil,
            "timezone": timezone,
            "float_compare": float_compare,
            "b64encode": base64.b64encode,
            "b64decode": base64.b64decode,
            "Command": Command,
            # orm
            "env": self.env,
            "model": self.env[self.model],
            # Exceptions
            "Warning": odoo.exceptions.Warning,
            "UserError": odoo.exceptions.UserError,
            # record
            "rule": self[:1],
            "record": records[:1],
            "records": records,
            "message": message,
            "partners": partners,
            # helpers
            "log": log,
        }
        if self.python_code:
            try:
                safe_eval(self.python_code, localdict, mode="exec", nocopy=True)
                message = localdict.get("message", message)
                partners = localdict.get("partners", partners)
            except Exception as e:
                _logger.warning(
                    f"Error evaluating Python code in rule '{self.name}': {e}"
                )
        return message, partners

    @api.model
    def notify_changes(self, partner_ids, message):
        """Send notification to partner_ids."""
        channel = "base_notification_updates"
        for partner_id in partner_ids:
            self.env["bus.bus"]._sendone(
                partner_id,
                channel,
                {
                    "message": message,
                },
            )

    def _execute_notification(self, records):
        """Send the configured notification."""
        if not self.active or not records:
            return
        if self.domain:
            try:
                domain = safe_eval(self.domain)
                records = records.filtered_domain(domain)
            except Exception as e:
                _logger.warning(
                    f"Invalid domain in rule {self.name}: {self.domain} ({e})"
                )
        message, partner_ids = self._get_dynamic_message_and_partners(records)
        self.notify_changes(partner_ids, message)
        if self.message_type == "chatter_log":
            for rec in records:
                rec.with_context(mail_post_autofollow=False).message_post(
                    body=message,
                    partner_ids=partner_ids.ids,
                )
        else:
            Mail = self.env["mail.mail"].sudo()
            for partner_id in partner_ids:
                mail_values = {
                    "subject": _("%(name)s - %(model)s | Notification")
                    % {
                        "name": self.name,
                        "model": self.model_id.name,
                    },
                    "body_html": message,
                    "recipient_ids": partner_id,
                    "auto_delete": True,
                    "is_notification": True,
                }
                Mail.create(mail_values).send()

    def _apply_trigger(self, event_type, records):
        """Called by create/write/unlink hooks."""
        rules = self.sudo().search(
            [
                ("model_id.model", "=", records._name),
                ("trigger", "=", event_type),
                ("active", "=", True),
            ]
        )
        for rule in rules:
            if rule.notify_mode == "queued":
                # Use queue job to send later
                record_ids_str = ", ".join(map(str, records.ids))
                description = _(
                    "Sending a queued notification for model: %(model)s (IDs: %(ids)s)"
                ) % {
                    "model": records._name,
                    "ids": record_ids_str,
                }
                rule.with_delay(
                    description=description, identity_key=identity_exact
                )._execute_notification(records)
            else:
                # Send immediately
                rule._execute_notification(records)
