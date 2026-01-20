# Copyright 2015 ABF OSIELL <https://osiell.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class AuditlogLog(models.Model):
    _name = "auditlog.log"
    _description = "Auditlog - Log"
    _order = "create_date desc"

    name = fields.Char("Resource Name", size=64)
    model_id = fields.Many2one(
        "ir.model", string="Model", index=True, ondelete="set null"
    )
    model_name = fields.Char(readonly=True)
    model_model = fields.Char(string="Technical Model Name", readonly=True)
    res_id = fields.Integer("Resource ID")
    res_ids = fields.Char("Resource IDs")
    user_id = fields.Many2one("res.users", string="User")
    method = fields.Char(size=64)
    line_ids = fields.One2many("auditlog.log.line", "log_id", string="Fields updated")
    http_session_id = fields.Many2one(
        "auditlog.http.session", string="Session", index=True
    )
    http_request_id = fields.Many2one(
        "auditlog.http.request", string="HTTP Request", index=True
    )
    log_type = fields.Selection(
        [("full", "Full log"), ("fast", "Fast log")], string="Type"
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Insert model_name and model_model field values upon creation."""
        for vals in vals_list:
            if not vals.get("model_id"):
                raise UserError(self.env._("No model defined to create log."))
            model = self.env["ir.model"].sudo().browse(vals["model_id"])
            vals.update({"model_name": model.name, "model_model": model.model})
        return super().create(vals_list)

    def write(self, vals):
        """Update model_name and model_model field values to reflect model_id
        changes."""
        if "model_id" in vals:
            if not vals["model_id"]:
                raise UserError(self.env._("The field 'model_id' cannot be empty."))
            model = self.env["ir.model"].sudo().browse(vals["model_id"])
            vals.update({"model_name": model.name, "model_model": model.model})
        return super().write(vals)

    def show_res_ids(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": self.model_id.model,
            "domain": [("id", "in", safe_eval(self.res_ids))],
            "name": self.env._("Exported Records"),
        }
