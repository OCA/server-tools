# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path

from odoo.addons.base.models.ir_model import MODULE_UNINSTALL_FLAG


class IrModelData(models.Model):
    _inherit = "ir.model.data"

    @api.model
    def _module_data_uninstall(self, modules_to_remove):
        """this function crashes for xmlids on undefined models or fields
        referring to undefined models"""
        for this in self.search([("module", "in", modules_to_remove)]):
            if this.model == "ir.model.fields":
                field = (
                    self.env[this.model]
                    .with_context(**{MODULE_UNINSTALL_FLAG: True})
                    .browse(this.res_id)
                )
                if not field.exists() or field.model not in self.env:
                    this.unlink()
                    continue
            if this.model not in self.env:
                this.unlink()
        return super(IrModelData, self)._module_data_uninstall(modules_to_remove)


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
        modules.filtered(
            lambda x: x.state not in ("uninstallable", "uninstalled")
        ).button_immediate_uninstall()
        modules.refresh()
        modules.unlink()
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
            if module.state == "uninstalled":
                self.env["cleanup.purge.line.module"].create(
                    {
                        "name": module.name,
                    }
                ).purge()
                continue
            res.append((0, 0, {"name": module.name}))

        if not res:
            raise UserError(_("No modules found to purge"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.module", "wizard_id", "Modules to purge"
    )
