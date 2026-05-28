# © 2023 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import uuid

from odoo import _, api, fields, models

_logger = logging.getLogger(__name__)


class Monitoring(models.Model):
    _name = "monitoring"
    _description = _("Monitoring definition")
    _inherit = ["monitoring.output.mixin"]

    def _get_states(self):
        return [
            ("unknown", _("Unknown")),
            ("ok", _("OK")),
            ("warning", _("Warning")),
            ("critical", _("Critical")),
        ]

    name = fields.Char()
    active = fields.Boolean(default=True)
    token = fields.Char(
        default=lambda self: str(uuid.uuid4()),
        readonly=True,
        copy=False,
        help="Token to use for the API",
    )
    script_ids = fields.Many2many("monitoring.script")
    state = fields.Selection("_get_states", default="unknown", compute="_compute_state")
    verbose = fields.Boolean(help="Send the information about all scripts")
    mail_sent = fields.Boolean()
    mail_template_id = fields.Many2one(
        "mail.template",
        domain=[("model", "=", "monitoring")],
        help="Set a mail template to send a mail if the state is warning or critical.",
    )

    _sql_constraints = [
        ("token_uniq", "UNIQUE(token)", _("The token must be unique")),
    ]

    @api.depends("script_ids", "script_ids.state", "script_ids.active")
    def _compute_state(self):
        for rec in self:
            states = rec.script_ids.filtered("active").mapped("state")
            if "critical" in states:
                rec.state = "critical"
            elif "warning" in states:
                rec.state = "warning"
            elif len(states):
                rec.state = "ok"
                rec.mail_sent = False
            else:
                rec.state = "unknown"

    def action_validate(self):
        self.validate(False)
        return {"type": "ir.actions.client", "tag": "reload"}

    def cron_validate(self, send_mail=True):
        for rec in self or self.search([]):
            rec.validate(send_mail)

    def validate(self, send_mail=False):
        self.ensure_one()

        result = self.script_ids.validate(self._use_verbose())

        if (
            send_mail
            and self.mail_template_id
            and self.state in ("critical", "warning")
            and not self.mail_sent
        ):
            self.mail_template_id.send_mail(self.id)
            self.mail_sent = True

        return result

    def validate_and_format(self, send_mail=False):
        self.ensure_one()

        result = self.validate(send_mail=send_mail)
        return self.format_output(result)

    def _use_verbose(self):
        return self.output_format == "prometheus" or self.verbose
