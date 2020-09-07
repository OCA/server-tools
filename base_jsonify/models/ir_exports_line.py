# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IrExportsLine(models.Model):
    _inherit = "ir.exports.line"

    alias = fields.Char(
        "Alias",
        help="The complete path to the field where you can specify an "
        "alias on the a step as field:alias",
    )
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
    function = fields.Char(
        comodel_name="ir.exports.resolver",
        string="Function",
        help="A method defined on the model that takes a record and a field_name",
    )

    @api.constrains("resolver_id", "function")
    def _check_function_resolver(self):
        for rec in self:
            if rec.resolver_id and rec.function:
                raise ValidationError(
                    _("Either set a function or a resolver, not both.")
                )

    @api.constrains("alias", "name")
    def _check_alias(self):
        for rec in self:
            if not rec.alias:
                continue
            names = rec.name.split("/")
            names_with_alias = rec.alias.split("/")
            if len(names) != len(names_with_alias):
                raise ValidationError(
                    _("Name and Alias must have the same hierarchy depth")
                )
            for name, name_with_alias in zip(names, names_with_alias):
                field_name = name_with_alias.split(":")[0]
                if name != field_name:
                    raise ValidationError(
                        _(
                            "The alias must reference the same field as in "
                            "name '%s' not in '%s'"
                        )
                        % (name, name_with_alias)
                    )
