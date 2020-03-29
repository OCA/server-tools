# Copyright 2016 Vauxoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging
import os

from odoo import _, api, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class CompanyCountryConfigSettings(models.AbstractModel):
    _name = "company.country.config.settings"
    _description = "Company Country Configuration Settings"

    @api.model
    def load_company_country(self, country_code=None):
        account_installed = self.env["ir.module.module"].search(
            [("name", "=", "account"), ("state", "=", "installed")], limit=1
        )
        if account_installed:
            # If the account module is installed, that means changing the
            # company's country will have no effect, as the account hook was
            # already run and an l10n module was already been installed
            _logger.info("account module already installed, skipping")
            return
        if not country_code:
            country_code = os.environ.get("COUNTRY")
        if country_code == "":
            self.env.ref("base.main_company").write({"country_id": False})
            return
        if not country_code:
            l10n_to_install = self.env["ir.module.module"].search(
                [("state", "=", "to install"), ("name", "=like", "l10n_%")], limit=1
            )
            if not l10n_to_install:
                raise ValidationError(
                    _(
                        "COUNTRY environment variable with country code is not "
                        "set and no localization module is marked to be "
                        "installed."
                    )
                )
            country_code = l10n_to_install.name.split("l10n_")[1][:2].upper()

        country = self.env["res.country"].search(
            [("code", "ilike", country_code)], limit=1
        )
        if not country:
            raise ValidationError(
                _(
                    "Country code %s was not found. Please use a valid two-letter "
                    "ISO 3166 code."
                )
            )
        self.env.ref("base.main_company").write({"country_id": country.id})
