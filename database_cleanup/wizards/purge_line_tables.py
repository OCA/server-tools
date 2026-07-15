# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from psycopg2.extensions import AsIs

from odoo import fields, models

from ..identifier_adapter import IdentifierAdapter

_TABLE_TYPE_SELECTION = [
    ("base", "SQL Table"),
    ("view", "SQL View"),
]


class CleanupPurgeLineTable(models.TransientModel):
    _inherit = "cleanup.purge.line"
    _name = "cleanup.purge.line.table"
    _description = "Cleanup Purge Line Table"

    wizard_id = fields.Many2one(
        "cleanup.purge.wizard.table", "Purge Wizard", readonly=True
    )
    table_type = fields.Selection(selection=_TABLE_TYPE_SELECTION)

    def purge(self):
        """
        Unlink tables upon manual confirmation.
        """
        if self:
            objs = self
        else:
            objs = self.env["cleanup.purge.line.table"].browse(
                self.env.context.get("active_ids")
            )
        for line in objs:
            if line.purged:
                continue

            if line.table_type == "base":
                _sql_type = "TABLE"
            elif line.table_type == "view":
                _sql_type = "VIEW"
            self.logger.info("Dropping %s %s", _sql_type, line.name)
            # CASCADE also drops the views, constraints and child tables which
            # depend on it; IF EXISTS skips a view already dropped that way
            self.env.cr.execute(
                "DROP %s IF EXISTS %s CASCADE",
                (AsIs(_sql_type), IdentifierAdapter(line.name)),
            )
            line.write({"purged": True})
        return True
