# Copyright 2022 Camptocamp SA, Trobz
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl)

from odoo import _, fields, models


class BaseSelection(models.Model):
    _name = "base.selection"
    _description = "Store values in db for more flexible with fields.Selection"
    _order = "field_id, sequence, id"
    field_id = fields.Many2one("ir.model.fields")
    code = fields.Char(index=True, required=True)
    name = fields.Char(translate=True, required=True)
    sequence = fields.Integer()
    active = fields.Boolean(default=True)
    default = fields.Boolean(default=False)
    _sql_constraints = [
        (
            "field_code_uniq",
            "UNIQUE(field_id, code)",
            _("Codes of the field must be unique"),
        )
    ]


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"
    base_selection_ids = fields.One2many("base.selection", "field_id")


class SelectionMixin(models.AbstractModel):
    _name = "base.selection.mixin"
    _description = "Helper methods to work with base.selection"

    def get_selection_domain(self, field_name):
        for_field_name = [
            ("model", "=", self._name),
            ("name", "=", field_name),
        ]
        IrModelFields = self.env["ir.model.fields"]
        field = IrModelFields.search(for_field_name)
        return [("field_id", "=", field.id)]

    def get_default_selection(self, field_name):
        Selection = self.env["base.selection"]
        for_defaut = self.get_selection_domain(field_name)
        for_defaut.append(("default", "=", True))
        selection = Selection.search(for_defaut, limit=1)
        return selection
