# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    restrict_update = fields.Boolean(
        "Update Restrict Model",
        help="When selected, the model is restricted to read-only unless the "
        "user has the special permission.",
    )
    skip_check_for_readonly_users = fields.Boolean(
        help="Allow readonly users to create/write/delete records of this model"
    )
