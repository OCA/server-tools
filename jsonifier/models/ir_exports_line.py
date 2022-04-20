# Copyright 2017 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IrExportsLine(models.Model):
    _inherit = "ir.exports.line"

    target = fields.Char(
        "Target",
        help="The complete path to the field where you can specify a "
        "target on the step as field:target",
    )
    active = fields.Boolean(string="Active", default=True)
    lang_id = fields.Many2one(
        comodel_name="res.lang",
        string="Language",
        help="If set, the language in which the field is exported",
    )
    resolver_id = fields.Many2one(
        comodel_name="ir.exports.resolver",
        string="Custom resolver",
        help="If set, will apply the resolver on the field value",
    )
    instance_method_name = fields.Char(
        string="Function",
        help="A method defined on the model that takes a record and a field_name",
    )

    @api.constrains("resolver_id", "instance_method_name")
    def _check_function_resolver(self):
        for rec in self:
            if rec.resolver_id and rec.instance_method_name:
                msg = _("Either set a function or a resolver, not both.")
                raise ValidationError(msg)

    @api.constrains("target", "name")
    def _check_target(self):
        for rec in self:
            if not rec.target:
                continue
            names = rec.name.split("/")
            names_with_target = rec.target.split("/")
            if len(names) != len(names_with_target):
                raise ValidationError(
                    _("Name and Target must have the same hierarchy depth")
                )
            for name, name_with_target in zip(names, names_with_target):
                field_name = name_with_target.split(":")[0]
                if name != field_name:
                    raise ValidationError(
                        _(
                            "The target must reference the same field as in "
                            "name '%s' not in '%s'"
                        )
                        % (name, name_with_target)
                    )
