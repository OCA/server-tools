# Copyright 2021 Therp B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AuditlogLineAccessRule(models.Model):
    _name = "auditlog.line.access.rule"

    name = fields.Char()

    field_ids = fields.Many2many("ir.model.fields")
    group_ids = fields.Many2many(
        "res.groups",
        help="""Groups that will be allowed to see the logged fields, if left empty
                default will be all users with a login""",
    )
    model_id = fields.Many2one(
        "ir.model", related="auditlog_rule_id.model_id", readonly=True
    )
    auditlog_rule_id = fields.Many2one(
        "auditlog.rule", "auditlog_access_rule_ids", readonly=True, ondelete="cascade"
    )
    state = fields.Selection(related="auditlog_rule_id.state", readonly=True)

    def needs_rule(self):
        self.ensure_one()
        return bool(self.group_ids)

    def get_linked_rules(self):
        return self.env["ir.rule"].search(
            [("auditlog_line_access_rule_id", "in", self.ids)]
        )

    def unlink(self):
        to_delete = self.get_linked_rules()
        res = super(AuditlogLineAccessRule, self).unlink()
        if res:
            res = res and to_delete.unlink()
        return res

    def add_default_group_if_needed(self):
        self.ensure_one()
        res = False
        if not self.group_ids and self.field_ids:
            res = self.with_context(no_iter=True).write(
                {"group_ids": [(6, 0, [self.env.ref("base.group_user").id])]}
            )
        return res

    @api.model
    def create(self, vals):
        res = super(AuditlogLineAccessRule, self).create(vals)
        res.add_default_group_if_needed()
        res.regenerate_rules()
        return res

    def write(self, vals):
        res = super(AuditlogLineAccessRule, self).write(vals)
        for this in self:
            added = this.add_default_group_if_needed()
            if (
                any(
                    [
                        x in vals
                        for x in ("group_ids", "field_ids", "model_id", "all_fields")
                    ]
                )
                or added
            ):
                this.regenerate_rules()

        return res

    def remove_rules(self):
        for this in self:
            this.get_linked_rules().unlink()

    def regenerate_rules(self):
        for this in self:
            this.remove_rules()
            dict_values = this._prepare_rule_values()
            for values in dict_values:
                self.env["ir.rule"].create(values)

    def _prepare_rule_values(self):
        self.ensure_one()
        if not self.needs_rule():
            return []
        domain_force = "[" + " ('log_id.model_id' , '=', %s)," % (self.model_id.id)
        if self.field_ids:
            domain_force = "[('field_id', 'in',  %s)]" % (self.field_ids.ids)
            model = self.env.ref("auditlog.model_auditlog_log_line")
        else:
            domain_force = "[('model_id', '=', %s)]" % (self.model_id.id)
            model = self.env.ref("auditlog.model_auditlog_log")
        auditlog_security_group = self.env.ref(
            "auditlog_security.group_can_view_audit_logs"
        )
        return [
            {
                "name": "auditlog_extended_%s" % self.id,
                "model_id": model.id,
                "groups": [(6, 0, self.group_ids.ids)],
                "perm_read": True,
                "domain_force": domain_force,
                "auditlog_line_access_rule_id": self.id,
            },
            {
                "name": "auditlog_extended_%s" % self.id,
                "model_id": model.id,
                "groups": [(6, 0, [auditlog_security_group.id])],
                "perm_read": True,
                "domain_force": [(1, "=", 1)],
                "auditlog_line_access_rule_id": self.id,
            },
        ]
