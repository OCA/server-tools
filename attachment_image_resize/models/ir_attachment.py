# Copyright 2024 Quartile
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

IMAGE_TYPES = ["image/png", "image/jpeg", "image/bmp", "image/tiff"]


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    resize_done = fields.Boolean(
        help="Indicates whether the resizing process has been run on this record. "
        "Once selected, the record will be excluded from "
        "the _cron_resize_attachment_image() target."
    )

    def _postprocess_contents(self, values):
        self = self.with_context(
            resize_target_model=values.get("res_model") or self.res_model
        )
        self.resize_done = True
        return super()._postprocess_contents(values)

    @api.model
    def _cron_resize_attachment_image(self, limit):
        model_list = (
            self.env["ir.model"]
            .search([("attachment_image_max_resolution", "!=", False)])
            .mapped("model")
        )
        if model_list:
            attachments = self.sudo().search(
                [
                    ("res_model", "in", model_list),
                    ("mimetype", "in", IMAGE_TYPES),
                    ("resize_done", "=", False),
                    # Added this filter because the default search only
                    # retrieves records with no res_field.
                    "|",
                    ("res_field", "=", False),
                    ("res_field", "!=", False),
                ],
                limit=limit,
            )
            for attachment in attachments:
                values = {
                    "datas": attachment.datas,
                    "mimetype": attachment.mimetype,
                    "res_model": attachment.res_model,
                }
                processed = attachment._postprocess_contents(values)
                if processed.get("datas") and processed["datas"] != attachment.datas:
                    attachment.write({"datas": processed["datas"]})
                attachment.resize_done = True
