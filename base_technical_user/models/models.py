# Copyright 2020 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, models
from odoo.exceptions import UserError


class Base(models.AbstractModel):
    _inherit = "base"

    def sudo_tech(self, raise_if_missing=False):
        self_sudoer = self
        tech_user = self.env.company.user_tech_id
        if tech_user:
            self_sudoer = self.with_user(tech_user.id)
            # We restrict the allowed companies to the one of the tech user
            allowed_company_ids = self.env.context.get("allowed_company_ids")
            # TODO: Is any(...) part necessary as we can consider company should always be
            # the one of the tech_user ?
            if allowed_company_ids and any(
                company
                for company in allowed_company_ids
                if company != tech_user.company_id.id
            ):
                self_sudoer = self_sudoer.with_context(
                    allowed_company_ids=self.env.company.ids
                )
        elif raise_if_missing:
            raise UserError(
                _("The technical user is missing in the company {}").format(
                    self.env.company.name
                )
            )
        return self_sudoer
