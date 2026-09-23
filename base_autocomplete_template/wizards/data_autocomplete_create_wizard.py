# Copyright 2026 (APSL-Nagarro) Bernat Obrador
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class DataAutocompleteCreateWizard(models.TransientModel):
    _name = "data.wizard.template.create"
    _description = "Create Template"

    name = fields.Char(required=True)
    model_id = fields.Many2one("ir.model", required=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
    )

    is_personal = fields.Boolean(
        string="Personal template",
        default=False,
        help="If enabled, only you will see this template.",
    )

    def action_create_template(self):
        self.ensure_one()

        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        if not active_model or not active_id:
            raise UserError(_("No active record found to build the template."))

        record = self.env[active_model].browse(active_id).exists()
        if not record:
            raise UserError(_("The source record no longer exists."))

        values = record._template_serialize()

        template = self.env["data.autocomplete.template"].create(
            {
                "name": self.name,
                "model_id": self.model_id.id,
                "company_id": self.company_id.id,
                "user_id": self.env.uid if self.is_personal else False,
                "values_json": "{}",
            }
        )
        template.set_values(values)

        # Reassign the template to the record if applicable
        if "template_id" in record._fields:
            record.template_id = template.id

        return {
            "type": "ir.actions.act_window",
            "res_model": record._name,
            "res_id": record.id,
            "view_mode": "form",
            "target": "new",
            "context": dict(self.env.context),
        }
