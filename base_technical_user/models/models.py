# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, models
from odoo.exceptions import UserError


class Base(models.AbstractModel):
    _inherit = "base"

    def sudo_tech(self, raise_if_missing=False):
        self_sudoer = self
        tech_user = self.env.user.company_id.user_tech_id
        if tech_user:
            self_sudoer = self.sudo(tech_user.id)
        elif raise_if_missing:
            raise UserError(
                _("The technical user is missing in the company {}").format(
                    self.env.user.company_id.name
                )
            )
        return self_sudoer
