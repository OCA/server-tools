# Copyright 2021 Therp BV <http://www.sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited

# NB: Dealing with RecursionError: Max no of Maximum Recursion Depth Exceeded
# -----------------------------------------------------------------------------
# Since we are using recursion, python has a recursive limit before it throws
# 'RecursionError' of max no of calls. We can simply randomly increase this
# limit however in large data menus can exceed the below set limit and leads to
# random additions. We could possible use for loop based on the 'n' menus to
# increase number of calls.
# ----------------------------------------------------------------------------
import sys

from odoo import _, api, fields, models
from odoo.exceptions import UserError

sys.setrecursionlimit(15000)


class CleanupPurgeLineMenuRel(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.menu.rel"
    _description = "Purge Parent Menu Rel Wizard Lines"

    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.menu.rel", "Purge Wizard", readonly=True
    )
    menu_id = fields.Many2one("ir.ui.menu", "Parent menu entry")

    def purge(self):
        """Unlink parent menu entries and children upon manual confirmation."""
        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.menu.rel"].browse(
                self._context.get("active_ids")
            )
        parent_menus = objs.filtered(lambda x: not x.purged and x.menu_id)
        self.logger.info(
            "Purging menu entries and " "their children: %s",
            parent_menus.mapped("name"),
        )
        for menu in parent_menus:
            # pass root menu
            self.recursive_purge([menu.menu_id])
            # record success
            menu.write({"purged": True})

    # Recursive purge of parent -> children
    #       --- (A) ---
    #       |    |    |
    #      (B)  (C)  (D)
    #            |
    #           (E)
    # This works well but python has a limit to the no of calls a recursion
    # can do. In design of this it is assumed the user will not purge all,
    # unless running migration script, in this case he/she should increase the
    # no of calls from sys.setrecursionlimit(10000) e.g 10000. Menus can be
    # a chain of hierarchy so if you know 'n' then set limit as per n or
    # n+10 whichever. Also probably a for loop of n would be ok though tricky.
    def recursive_purge(self, purge_lst):
        # boundary condition to break out of the recursion
        if not any(purge_lst):
            return True
        menu = purge_lst.pop()
        child_menus = (
            self.env["ir.ui.menu"]
            .with_context({"ir.ui.menu.full_list": True, "active_test": False})
            .search([("parent_path", "ilike", "{}/%".format(menu.id))])
        )
        menu.unlink()
        if child_menus:
            new = [x for x in child_menus]
            purge_lst += new
        return self.recursive_purge(purge_lst)


class CleanupPurgeWizardMenuitem(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.menu.rel"
    _description = "Purge parent menu and their child relations"

    @api.model
    def find(self):
        """
        Search for parent menus and their children and Purge them.
        """
        res = []
        # Get all menus who don't have parent set.
        parent_menus = (
            self.env["ir.ui.menu"]
            .with_context({"ir.ui.menu.full_list": True, "active_test": False})
            .search([("parent_id", "=", False), ("action", "=", False)])
        )
        for menu in parent_menus:
            res.append((0, 0, {"name": menu.complete_name, "menu_id": menu.id}))
        if not res:
            raise UserError(_("No dangling parent menus entries found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.menu.rel", "wizard_id", "Parent menu to purge"
    )
