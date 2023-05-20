# Copyright 2021 Quartile Limited
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResUsers(models.Model):
    _inherit = "res.users"

    unrestrict_model_update = fields.Boolean(
        help="Set to true and the user can update restricted model.",
    )
    is_readonly_user = fields.Boolean(
        "Ready User",
        help="Set to true and the user are readonly user on all models",
    )

    @api.constrains("is_readonly_user")
    def _check_is_readonly_user(self):
        for user in self:
            if self.env.ref("base.group_system") in user.groups_id:
                raise UserError(_("You cannot set admin user as a readonly user."))
