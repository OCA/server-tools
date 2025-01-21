# Copyright (C) 2018 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import api, exceptions, fields, models


class VacuumRule(models.Model):
    _name = "vacuum.rule"
    _description = "Rules Used to delete message historic"

    name = fields.Char(required=True)
    ttype = fields.Selection(
        selection=[("attachment", "Attachment"), ("message", "Message")],
        string="Type",
        required=True,
    )
    filename_pattern = fields.Char(
        help=("If set, only attachments containing this pattern will be" " deleted.")
    )
    inheriting_model = fields.Char(
        help="If set, this model will be searched and only related attachments will "
        "be deleted.\n\nN.B: model must implement _inherits to link ir.attachment"
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    message_subtype_ids = fields.Many2many(
        "mail.message.subtype",
        string="Subtypes",
        help="Message subtypes concerned by the rule. If left empty, the "
        "system won't take the subtype into account to find the "
        "messages to delete",
    )
    empty_subtype = fields.Boolean(
        help="Take also into account messages with no subtypes"
    )
    model_ids = fields.Many2many(
        "ir.model",
        string="Models",
        help="Models concerned by the rule. If left empty, it will take all "
        "models into account",
    )
    model_id = fields.Many2one(
        "ir.model",
        compute="_compute_model_id",
        help="Technical field used to set attributes (invisible/required, "
        "domain, etc...for other fields, like the domain filter",
    )
    model_filter_domain = fields.Text()
    model = fields.Char(compute="_compute_model_id", string="Model code")
    empty_model = fields.Boolean(
        help="Take into account attachment not linked to any model, but only if a "
        "pattern is set, to avoid deleting attachments generated/needed by odoo"
    )
    message_type = fields.Selection(
        [
            ("email", "Email"),
            ("comment", "Comment"),
            ("notification", "System notification"),
            ("user_notification", "User Specific Notification"),
            ("all", "All"),
        ]
    )
    retention_time = fields.Integer(
        required=True,
        default=365,
        help="Number of days the messages concerned by this rule will be "
        "keeped in the database after creation. Once the delay is "
        "passed, they will be automatically deleted.",
    )
    active = fields.Boolean(default=True)
    description = fields.Text()

    @api.depends("model_ids")
    def _compute_model_id(self):
        for rule in self:
            model_id = False
            model = False

            if rule.model_ids and len(rule.model_ids) == 1:
                model_id = rule.model_ids.id
                model = rule.model_id.model

            rule.model_id = model_id
            rule.model = model

    @api.constrains("retention_time")
    def retention_time_not_null(self):
        for rule in self:
            if not rule.retention_time:
                raise exceptions.ValidationError(
                    self.env._("The Retention Time can't be 0 days")
                )

    @api.constrains("inheriting_model")
    def _check_inheriting_model(self):
        for rule in self.filtered(lambda r: r.inheriting_model):
            if rule.ttype != "attachment":
                raise exceptions.ValidationError(
                    self.env._(
                        "Inheriting model cannot be used on "
                        "rule where type is not attachment"
                    )
                )
            if (
                rule.inheriting_model
                not in self.env["ir.attachment"]._inherits_children
            ):
                raise exceptions.ValidationError(
                    self.env._(
                        "No inheritance of ir.attachment "
                        f"was found on model {rule.inheriting_model}"
                    )
                )
            attachment_field = self.env[rule.inheriting_model]._inherits.get(
                "ir.attachment"
            )
            if not attachment_field:
                raise exceptions.ValidationError(
                    self.env._(
                        "Cannot find relation to ir.attachment "
                        f"on model {rule.inheriting_model}"
                    )
                )

    def _search_autovacuum_records(self):
        self.ensure_one()
        model = self.ttype
        if model == "message":
            model = "mail.message"
        elif model == "attachment":
            model = "ir.attachment"
        return self.env[model]._get_autovacuum_records(self)
