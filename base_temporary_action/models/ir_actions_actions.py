# Copyright 2025 ACSONE SA/NV
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class IrActionsActions(models.Model):
    _inherit = "ir.actions.actions"

    is_temporary = fields.Boolean()

    @api.autovacuum
    def _gc_temporary_actions(self):
        self.search(
            [
                ("is_temporary", "=", True),
                (
                    "create_date",
                    "<",
                    fields.Datetime.now()
                    - relativedelta(hours=self._transient_max_hours),
                ),
            ]
        ).unlink()
