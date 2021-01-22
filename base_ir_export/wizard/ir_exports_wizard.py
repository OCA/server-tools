from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IrExportsWizard(models.TransientModel):
    _name = "ir.exports.wizard"
    _description = "Create an Export"

    model_id = fields.Many2one(comodel_name="ir.model")
    model_name = fields.Char(
        string="Model Name", related="model_id.model", readonly=True,
    )
    name = fields.Char()
    export_field_ids = fields.Many2many(comodel_name="ir.model.fields",)

    @api.onchange("model_id")
    def _onchange_attribute_id_clean_value(self):
        return {"domain": {"export_field_ids": [("model_id", "=", self.model_id.id)]}}

    def create_ir_export(self):
        self._create_ir_export()

    def _create_ir_export(self):
        model = self.env[self.model_name]
        fields = self.export_field_ids
        missing_fields = [f for f in fields if f.name not in model._fields]
        if missing_fields:
            message = "The following fields are not defined on model {}: {}"
            raise ValidationError(_(message).format(self.model_name, missing_fields))
        export_vals = {
            "name": self.name or _("{} Export").format(self.model_name),
            "resource": self.model_name,
            "export_fields": [(0, 0, {"name": f.name}) for f in self.export_field_ids],
        }
        return self.env["ir.exports"].create(export_vals)
