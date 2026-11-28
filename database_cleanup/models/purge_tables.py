# Copyright 2014-2016 Therp BV <http://therp.nl>
# Copyright 2021 Camptocamp <https://camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models
from odoo.exceptions import UserError

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
                self._context.get("active_ids")
            )
        for line in objs:
            if line.purged:
                continue

            if line.table_type == "base":
                _sql_type = "TABLE"
            elif line.table_type == "view":
                _sql_type = "VIEW"
            self.logger.info("Dropping %s %s", _sql_type, line.name)
            # CASCADE removes dependent views, constraints and child tables first
            self.env.cr.execute(
                "DROP %s IF EXISTS %s CASCADE",
                (AsIs(_sql_type), IdentifierAdapter(line.name)),
            )
            line.write({"purged": True})
        return True


class CleanupPurgeWizardTable(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.table"
    _description = "Purge tables"

    blacklist = [
        "endpoint_route",  # web-api/endpoint_route_handler
    ]

    @api.model
    def find(self):
        """
        Search for tables and views that cannot be instantiated.
        """
        known_tables = list(self.blacklist)
        for model in self.env["ir.model"].search([]):
            if model.model not in self.env:
                continue
            model_pool = self.env[model.model]
            known_tables.append(model_pool._table)
            known_tables += [
                column.relation
                for column in model_pool._fields.values()
                if column.type == "many2many"
                and (column.compute is None or column.store)
                and column.relation
            ]

        self.env.cr.execute(
            """
            SELECT table_name, table_type FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_type in ('BASE TABLE', 'VIEW')
            AND table_name NOT IN %s""",
            (tuple(known_tables),),
        )

        res = [
            (
                0,
                0,
                {"name": row[0], "table_type": "view" if row[1] == "VIEW" else "base"},
            )
            for row in self.env.cr.fetchall()
        ]
        if not res:
            raise UserError(_("No orphaned tables found"))
        return res

    purge_line_ids = fields.One2many(
        "cleanup.purge.line.table", "wizard_id", "Tables to purge"
    )
