# © 2016 Opener B.V. (<https://opener.am>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import models


class Base(models.AbstractModel):
    _inherit = "base"

    def user_has_groups(self, groups):
        """To allow bypass group check (if any) when approve request,
        which inturn approve child documents"""
        if self.env.context.get("bypass_check_user_has_groups"):
            return True
        return super().user_has_groups(groups)
