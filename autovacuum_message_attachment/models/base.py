# Copyright (C) 2019 Akretion
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from odoo import fields, models


class Base(models.AbstractModel):
    _inherit = "base"

    assigned_attachment_ids = fields.One2many(
        "ir.attachment",
        "res_id",
        string="Assigned Attachments",
        domain=lambda self: [("res_model", "=", self._name)],
        auto_join=True,
    )
