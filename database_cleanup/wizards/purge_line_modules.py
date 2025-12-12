# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import fields, models


class CleanupPurgeLineModule(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.module"
    _description = "Cleanup Purge Line Module"

    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.module", "Purge Wizard", readonly=True
    )

    def purge(self):
        """
        Uninstall modules upon manual confirmation, then reload
        the database.
        """
        module_names = self.filtered(lambda x: not x.purged).mapped("name")
        modules = self.env["ir.module.module"].search([("name", "in", module_names)])
        if not modules:
            return True
        self.logger.info("Purging modules %s", ", ".join(module_names))
        installed = modules.filtered(lambda x: x.state in ("installed", "to upgrade"))
        to_remove = modules - installed
        to_remove += to_remove.downstream_dependencies()
        to_remove.write({"state": "to remove"})
        installed.button_immediate_uninstall()
        with self.env.registry.cursor() as new_cr:
            self.env(cr=new_cr)["ir.module.module"].browse(modules.ids).unlink()
        return self.write({"purged": True})
