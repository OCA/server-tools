# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import fields, models


class CleanupPurgeLineMenu(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.menu"
    _description = "Cleanup Purge Line Menu"

    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.menu", "Purge Wizard", readonly=True
    )
    menu_id = fields.Many2one("ir.ui.menu", "Menu entry")

    def purge(self):
        """Unlink menu entries upon manual confirmation."""
        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.menu"].browse(
                self._context.get("active_ids")
            )
        to_unlink = objs.filtered(lambda x: not x.purged and x.menu_id)
        self.logger.info("Purging menu entries: %s", to_unlink.mapped("name"))
        to_unlink.mapped("menu_id").unlink()
        return to_unlink.write({"purged": True})
