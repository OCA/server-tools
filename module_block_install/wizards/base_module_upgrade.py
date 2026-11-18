# Copyright 2026 Trobz
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class BaseModuleUpgrade(models.TransientModel):
    _inherit = "base.module.upgrade"

    def upgrade_module(self):
        Module = self.env["ir.module.module"]
        pending = Module.search(
            [("state", "in", ("to install", "to upgrade", "to remove"))]
        )
        if pending:
            Module._module_block_install_check("apply", "upgrade_module", pending)
        return super().upgrade_module()
