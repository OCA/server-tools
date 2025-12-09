# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path


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


class CleanupPurgeWizardModule(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.module"
    _description = "Purge modules"

    @api.model
    def find(self):
        res = []
        IrModule = self.env["ir.module.module"]
        for module in IrModule.search(
            [("to_buy", "=", False), ("name", "!=", "studio_customization")]
        ):
            if get_module_path(module.name, display_warning=False):
                continue
            res.append((0, 0, {"name": module.name}))

        if not res:
            raise UserError(self.env._("No modules found to purge"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.module", "wizard_id", "Modules to purge"
    )
