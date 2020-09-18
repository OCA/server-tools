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
    active = fields.Boolean(string="Active", default=True)

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
