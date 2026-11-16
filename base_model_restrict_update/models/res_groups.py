# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models
from odoo.exceptions import UserError


class ResGroups(models.Model):
    _inherit = "res.groups"

    @api.constrains("user_ids", "implied_ids")
    def _check_is_readonly_user(self):
        group_system = self.env.ref("base.group_system")
        if group_system not in self.all_implied_ids:
            return
        if self.env["res.users"].search_count(
            [
                ("is_readonly_user", "=", True),
                ("all_group_ids", "in", group_system.ids),
            ],
            limit=1,
        ):
            raise UserError(self.env._("You cannot make the admin user read-only."))
