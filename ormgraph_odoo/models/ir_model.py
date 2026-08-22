# --------------------------------------------------------------------------
# ORMGraph for Odoo — Live Architecture & ERD Studio
# Author: Piyush Kumar (iam-piyush)
# Website: https://iampiyush.one
# Description: Interactive ORM architecture intelligence, visual ERDs, and
#              relational dependency pathfinding for Odoo models.
# License: LGPL-3 (https://www.gnu.org/licenses/lgpl-3.0.html)
# --------------------------------------------------------------------------

from odoo import models


class IrModel(models.Model):
    _inherit = "ir.model"

    def action_view_ormgraph(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_url",
            "url": f"/ormgraph/studio?focus={self.model}",
            "target": "new",
        }
