# Copyright 2024 Akretion (https://www.akretion.com).
# @author Mathieu Delva <mathieu.delva@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    def _onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super()._onchange_template_id(
            template_id, composition_mode, model, res_id
        )
        attachment_id = False
        template_id = self.template_id.export_template_id
        if template_id:
            attachment_id = self._export_xlsx_from_export_template(
                model, res_id, template_id
            )
        if attachment_id:
            if "attachment_ids" in res["value"]:
                res["value"]["attachment_ids"][0][2].append(attachment_id.id)
            else:
                res["value"]["attachment_ids"] = [(6, 0, [attachment_id.id])]
        return res

    def _export_xlsx_from_export_template(self, model, res_id, template_id):
        export_wizard_model = self.env["export.xlsx.wizard"]
        self.env.context = dict(self.env.context)
        self.env.context.update(
            {
                "template_domain": [
                    ("res_model", "=", model),
                    ("fname", "=", template_id.fname),
                    ("gname", "=", False),
                ]
            }
        )
        export_wizard = export_wizard_model.create(
            {
                "res_ids": str(res_id),
                "res_model": model,
            }
        ).action_export()

        export_wizard = export_wizard_model.browse(export_wizard["res_id"])
        attachment_id = self.env["ir.attachment"].create(
            {
                "name": export_wizard.name,
                "type": "binary",
                "datas": export_wizard.data,
                "res_model": "mail.compose.message",
            }
        )
        return attachment_id
