# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class CleanupPurgeLineData(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.data"
    _description = "Cleanup Purge Line Data"

    data_id = fields.Many2one("ir.model.data", "Data entry")
    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.data", "Purge Wizard", readonly=True
    )

    def purge(self):
        """Unlink data entries upon manual confirmation."""
        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.data"].browse(
                self._context.get("active_ids")
            )
        to_unlink = objs.filtered(lambda x: not x.purged and x.data_id)
        self.logger.info("Purging data entries: %s", to_unlink.mapped("name"))
        to_unlink.mapped("data_id").unlink()
        return to_unlink.write({"purged": True})
