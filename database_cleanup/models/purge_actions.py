# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeLineAction(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.action"
    _description = "Purge Window Action Lines"

    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.action", "Purge Wizard", readonly=True
    )
    action_id = fields.Many2one("ir.actions.act_window", "Window action")

    def purge(self):
        """Unlink action entries upon manual confirmation."""
        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.action"].browse(
                self._context.get("active_ids")
            )
        to_unlink = objs.filtered(lambda x: not x.purged and x.action_id)
        self.logger.info("Purging window action entries: %s", to_unlink.mapped("name"))
        to_unlink.mapped("action_id").unlink()
        return to_unlink.write({"purged": True})


class CleanupPurgeWizardMenu(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.action"
    _description = "Purge Window Actions"

    @api.model
    def find(self):
        """
        Search for actions referring to non existent models
        """
        res = []
        for action in (
            self.env["ir.actions.act_window"]
            .with_context(active_test=False)
            .search([("res_model", "!=", False)])
        ):
            if action.type != "ir.actions.act_window":
                continue
            if (action.res_model and action.res_model not in self.env) or (
                action.binding_model_id.model
                and action.binding_model_id.model not in self.env
            ):
                res.append((0, 0, {"name": action.name, "action_id": action.id}))
        if not res:
            raise UserError(_("No obsolete Window Actions found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.action", "wizard_id", "Window Actions to purge"
    )
