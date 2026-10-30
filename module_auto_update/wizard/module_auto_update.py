from odoo import fields, models


class ModuleAutoUpdate(models.TransientModel):
    _name = "module.auto.update"
    _description = "Auto-Upgrade Modules"

    modules_to_update_ids = fields.Many2many(
        "ir.module.module", string="Modules to Update", readonly=True
    )

    def action_get_modules_to_update(self):
        self.modules_to_update_ids = self.env[
            "ir.module.module"
        ]._get_modules_with_changed_checksum()
        return {
            "type": "ir.actions.act_window",
            "res_model": "module.auto.update",
            "view_mode": "form",
            "res_id": self.id,
            "views": [(False, "form")],
            "target": "new",
        }

    def action_upgrade_module(self):
        self.env["ir.module.module"].upgrade_changed_checksum()
