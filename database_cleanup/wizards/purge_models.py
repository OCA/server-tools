# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeWizardModel(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.model"
    _description = "Purge models"

    @api.model
    def find(self):
        """
        Search for models that cannot be instantiated.
        """
        res = []
        self.env.cr.execute("SELECT model from ir_model")
        for (model,) in self.env.cr.fetchall():
            if model not in self.env:
                res.append((0, 0, {"name": model}))
        if not res:
            raise UserError(self.env._("No orphaned models found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.model", "wizard_id", "Models to purge"
    )
