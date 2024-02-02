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
        tables = objs.mapped("name")
        for line in objs:
            if line.purged:
                continue

            # Retrieve constraints on the tables to be dropped
            # This query is referenced in numerous places
            # on the Internet but credits probably go to Tom Lane
            # in this post http://www.postgresql.org/\
            # message-id/22895.1226088573@sss.pgh.pa.us
            # Only using the constraint name and the source table,
            # but I'm leaving the rest in for easier debugging
            self.env.cr.execute(
                """
                SELECT conname, confrelid::regclass, af.attname AS fcol,
                    conrelid::regclass, a.attname AS col
                FROM pg_attribute af, pg_attribute a,
                    (SELECT conname, conrelid, confrelid,conkey[i] AS conkey,
                         confkey[i] AS confkey
                     FROM (select conname, conrelid, confrelid, conkey,
                       confkey, generate_series(1,array_upper(conkey,1)) AS i
                       FROM pg_constraint WHERE contype = 'f') ss) ss2
                WHERE af.attnum = confkey AND af.attrelid = confrelid AND
                a.attnum = conkey AND a.attrelid = conrelid
                AND confrelid::regclass = '%s'::regclass;
                """,
                (IdentifierAdapter(line.name, quote=False),),
            )

            for constraint in self.env.cr.fetchall():
                if constraint[3] in tables:
                    self.logger.info(
                        "Dropping constraint %s on table %s (to be dropped)",
                        constraint[0],
                        constraint[3],
                    )
                    self.env.cr.execute(
                        "ALTER TABLE %s DROP CONSTRAINT %s",
                        (
                            IdentifierAdapter(constraint[3]),
                            IdentifierAdapter(constraint[0]),
                        ),
                    )

            if line.table_type == "base":
                _sql_type = "TABLE"
            elif line.table_type == "view":
                _sql_type = "VIEW"
            self.logger.info("Dropping %s %s", _sql_type, line.name)
            self.env.cr.execute(
                "DROP %s %s", (AsIs(_sql_type), IdentifierAdapter(line.name))
            )
            line.write({"purged": True})
        return True


class CleanupPurgeWizardTable(models.TransientModel):
    _inherit = "cleanup.purge.wizard"
    _name = "cleanup.purge.wizard.table"
    _description = "Purge tables"

    @api.model
    def find(self):
        """
        Search for tables and views that cannot be instantiated.
        """
        known_tables = []
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
