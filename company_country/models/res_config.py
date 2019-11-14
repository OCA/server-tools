# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import os

from odoo import _, api, models
from odoo.exceptions import ValidationError


class CompanyCountryConfigSettings(models.TransientModel):
    _name = "company.country.config.settings"
    _description = "Company Country Configuration Settings"

    @api.model
    def load_company_country(self, country_code=None):
        if not country_code:
            country_code = os.environ.get("COUNTRY")
        if country_code == "":
            self.env.ref("base.main_company").write({"country_id": None})
            return
        if not country_code:
            l10n_to_install = self.env["ir.module.module"].search(
                [("state", "=", "to install"), ("name", "=like", "l10n_%")], limit=1
            )
            if not l10n_to_install:
                raise ValidationError(
                    _(
                        "Error COUNTRY environment variable with country code "
                        "not defined and no localization found in pool."
                    )
                )
            country_code = l10n_to_install.name.split("l10n_")[1][:2].upper()

        country = self.env["res.country"].search(
            [("code", "ilike", country_code)], limit=1
        )
        if not country:
            raise ValidationError(
                _("Country code %s not found. Use ISO 3166 codes 2 letters")
            )
        self.env.ref("base.main_company").write({"country_id": country.id})
