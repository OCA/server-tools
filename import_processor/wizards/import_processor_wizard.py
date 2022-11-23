# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import _, api, fields, models


class ImporterProcessorWizard(models.TransientModel):
    _name = "import.processor.wizard"
    _description = _("Import Processor Wizard")

    model = fields.Char()
    processor_id = fields.Many2one(
        "import.processor",
        domain='[("model_name", "=", model)]',
    )
    file_upload = fields.Binary()
    message = fields.Text(readonly=True)

    @api.onchange("model")
    def onchange_model(self):
        processor = (
            self.env["import.processor"]
            .sudo()
            .search([("model_name", "=", self.model)])
        )

        if len(processor) == 1:
            self.processor_id = processor.id

    def action_import(self):
        self.ensure_one()
        records = self.processor_id.process(base64.decodebytes(self.file_upload))
        return {
            "type": "ir.actions.act_window",
            "name": _("Import Processor"),
            "target": "new",
            "view_mode": "form",
            "res_model": self._name,
            "context": {
                "default_model": self.model,
                "default_message": _("Imported %s record(s)") % len(records),
                "default_processor_id": self.processor_id.id,
            },
        }
