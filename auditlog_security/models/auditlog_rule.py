# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class AuditlogRule(models.Model):
    _inherit = "auditlog.rule"

    auditlog_line_access_rule_ids = fields.One2many(
        "auditlog.line.access.rule", "auditlog_rule_id", ondelete="cascade"
    )
    server_action_id = fields.Many2one(
        "ir.actions.server",
        "Server Action",
    )
    log_selected_fields_only = fields.Boolean(
        default=True,
        help="Log only the selected fields, to save space avoid large DB data.",
    )

    @api.constrains("model_id")
    def unique_model(self):
        if self.search_count([("model_id", "=", self.model_id.id)]) > 1:
            raise ValidationError(_("A rule for this model already exists"))

    @api.model
    @tools.ormcache("model_name")
    def _get_field_names_of_rule(self, model_name):
        """Memory-cached list of fields per rule"""
        rule = (
            self.env["auditlog.rule"]
            .sudo()
            .search([("model_id.model", "=", model_name)], limit=1)
        )
        if rule.auditlog_line_access_rule_ids:
            return rule.mapped("auditlog_line_access_rule_ids.field_ids.name")
        return []

    @api.model
    @tools.ormcache("model_name")
    def _get_log_selected_fields_only(self, model_name):
        """Memory-cached translation of model to rule"""
        rule = (
            self.env["auditlog.rule"]
            .sudo()
            .search([("model_id.model", "=", model_name)], limit=1)
        )
        return rule.log_selected_fields_only

    @api.model
    def get_auditlog_fields(self, model):
        res = super(AuditlogRule, self).get_auditlog_fields(model)
        if self._get_log_selected_fields_only(model._name):
            selected_field_names = self._get_field_names_of_rule(model._name)
            # we re-use the checks on non-stored fields from super.
            res = [x for x in selected_field_names if x in res]
        return res

    @api.multi
    def write(self, values):
        cache_invalidating_fields = [
            "state",
            "auditlog_line_access_rule_ids",
            "log_selected_fields_only",
        ]
        if any([field in values.keys() for field in cache_invalidating_fields]):
            # clear cache for all ormcache methods.
            self.clear_caches()
        return super(AuditlogRule, self).write(values)

    @api.onchange("model_id")
    def onchange_model_id(self):
        # if model changes we must wipe out all field ids
        self.auditlog_line_access_rule_ids.unlink()

    @api.model
    def _get_view_log_lines_action(self):
        assert self.env.context.get("active_model")
        assert self.env.context.get("active_ids")
        model = (
            self.env["ir.model"]
            .sudo()
            .search([("model", "=", self.env.context.get("active_model"))])
        )
        domain = [
            ("model_id", "=", model.id),
            ("res_id", "in", self.env.context.get("active_ids")),
        ]
        return {
            "name": _("View Log Lines"),
            "res_model": "auditlog.log.line",
            "view_mode": "tree,form",
            "view_id": False,
            "domain": domain,
            "type": "ir.actions.act_window",
        }

    @api.multi
    def _create_server_action(self):
        self.ensure_one()
        code = "action = env['auditlog.rule']._get_view_log_lines_action()"
        server_action = (
            self.env["ir.actions.server"]
            .sudo()
            .create(
                {
                    "name": "View Log Lines",
                    "model_id": self.model_id.id,
                    "state": "code",
                    "code": code,
                }
            )
        )
        self.write({"server_action_id": server_action.id})
        return server_action

    @api.multi
    def subscribe(self):
        for rule in self:
            server_action = rule._create_server_action()
            server_action.create_action()
        res = super(AuditlogRule, self).subscribe()
        for rule in self:
            rule.auditlog_line_access_rule_ids.regenerate_rules()
        # rule now will have "View Log" Action, make that visible only for admin
        if res:
            self.action_id.write(
                {"groups_id": [(6, 0, [self.env.ref("base.group_system").id])]}
            )
        return res

    @api.multi
    def unsubscribe(self):
        for rule in self:
            rule.auditlog_line_access_rule_ids.remove_rules()
        for rule in self:
            rule.server_action_id.unlink()
        return super(AuditlogRule, self).unsubscribe()
