# Copyright (C) 2022 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models

RESTRICT_DELETE_ATTACH = [
    ("strict", "Strict: Only creator and admin can delete them"),
    ("custom", "Custom: For each model, selected groups and users can delete them"),
    ("none", "No restriction: All users / groups can delete them"),
]


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    restrict_delete_attachment = fields.Selection(
        selection=RESTRICT_DELETE_ATTACH,
        readonly=False,
        required=True,
        default="strict",
    )
