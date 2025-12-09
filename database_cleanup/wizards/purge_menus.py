# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeWizardMenu(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.menu"
    _description = "Purge menus"

    @api.model
    def find(self):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        for menu in (
            self.env["ir.ui.menu"]
            .with_context(active_test=False)
            .search([("action", "!=", False)])
        ):
            if menu.action.type != "ir.actions.act_window":
                continue
            if menu.action.res_model and menu.action.res_model not in self.env:
                res.append(
                    (
                        0,
                        0,
                        {
                            "name": menu.complete_name,
                            "menu_id": menu.id,
                        },
                    )
                )
        if not res:
            raise UserError(self.env._("No dangling menu entries found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.menu", "wizard_id", "Menus to purge"
    )
