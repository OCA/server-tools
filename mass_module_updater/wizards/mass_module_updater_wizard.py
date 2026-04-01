# Copyright 2026 Pol Reig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class MassModuleUpdaterWizard(models.TransientModel):
    _name = "mass.module.updater.wizard"
    _description = "Mass Module Updater Wizard"

    module_names = fields.Char(
        required=True, help="Comma-separated list of module names."
    )

    def _get_modules(self):
        raw_names = self.module_names.split(",")
        module_names = [name.strip() for name in raw_names if name.strip()]

        if not module_names:
            raise UserError(_("Please provide at least one valid module name."))

        modules = self.env["ir.module.module"].search([("name", "in", module_names)])

        found_names = set(modules.mapped("name"))
        missing_names = set(module_names) - found_names
        if missing_names:
            raise UserError(
                _(
                    "The following modules were not found: %s",
                    ", ".join(sorted(missing_names)),
                )
            )
        return modules

    def action_install_modules(self):
        self.ensure_one()
        modules = self._get_modules()
        already_installed = modules.filtered(lambda m: m.state == "installed")
        if already_installed:
            raise UserError(
                _(
                    "The following modules are already installed: %s",
                    ", ".join(sorted(already_installed.mapped("name"))),
                )
            )
        return modules.button_immediate_install()

    def action_update_modules(self):
        self.ensure_one()
        modules = self._get_modules()
        uninstalled = modules.filtered(lambda m: m.state != "installed")
        if uninstalled:
            raise UserError(
                _(
                    "The following modules are not installed: %s",
                    ", ".join(sorted(uninstalled.mapped("name"))),
                )
            )
        return modules.button_immediate_upgrade()
