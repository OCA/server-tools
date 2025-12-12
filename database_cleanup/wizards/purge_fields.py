# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models
from odoo.exceptions import UserError


class CleanupPurgeWizardField(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.field"
    _description = "Purge fields"

    @api.model
    def find(self):
        """
        Search for fields not technically mapped to a model.
        """
        res = []
        ignored_fields = models.MAGIC_COLUMNS + [
            "display_name",
        ]
        domain = [("state", "=", "base")]
        for field_id in self.env["ir.model.fields"].search(domain):
            if field_id.name in ignored_fields:
                continue
            model = self.env[field_id.model_id.model]
            if field_id.name not in model._fields.keys():
                res.append(
                    (
                        0,
                        0,
                        {
                            "name": field_id.name,
                            "field_id": field_id.id,
                        },
                    )
                )
        if not res:
            raise UserError(self.env._("No orphaned fields found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.field", "wizard_id", "Fields to purge"
    )
