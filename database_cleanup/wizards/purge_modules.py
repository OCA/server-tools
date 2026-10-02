# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.modules.module import get_module_path


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
