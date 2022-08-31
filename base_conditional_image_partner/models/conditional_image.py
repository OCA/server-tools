# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class ConditionalImage(models.Model):
    _inherit = "conditional.image"

    @api.model
    def create(self, val_list):
        image = super().create(val_list)
        image.reset_company_logo_web_for_partner()
        return image

    def write(self, vals):
        result = super().write(vals)
        self.reset_company_logo_web_for_partner()
        return result

    def reset_company_logo_web_for_partner(self):
        """
        Reset the company field logo_web for each related partner matching the image criteria
        """
        partner_model = self.env["res.partner"]
        company_model = self.env["res.company"]
        for record in self.filtered(lambda rec: rec.model_name == "res.partner"):
            partners = partner_model.search([]).filtered(
                lambda rec: rec._conditional_image_evaluate_selector(record)
            )
            companies = company_model.search([("partner_id", "in", partners.ids)])
            companies._compute_logo_web()  # make call otherwise it render the default image
