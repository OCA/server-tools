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
                self._context.get("active_ids")
            )
        for line in objs:
            if line.purged:
                continue
            line._drop_constraints(objs)
            line._drop_dependent_views(objs)

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

    def _drop_constraints(self, lines):
        self.ensure_one()
        # Retrieve constraints on the tables to be dropped
        # This query is referenced in numerous places
        # on the Internet but credits probably go to Tom Lane
        # in this post http://www.postgresql.org/\
        # message-id/22895.1226088573@sss.pgh.pa.us
        # Only using the constraint name and the source table,
        # but I'm leaving the rest in for easier debugging
        tables = lines.mapped("name")
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
            (IdentifierAdapter(self.name, quote=False),),
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

    def _drop_dependent_views(self, lines):
        self.ensure_one()
        self.env.cr.execute(
            """
            SELECT
                DISTINCT dependent_view.relname
            FROM pg_depend dep
            JOIN pg_rewrite rw
                ON dep.objid = rw.oid
            JOIN pg_class dependent_view
                ON rw.ev_class = dependent_view.oid
            JOIN pg_class source_table
                ON dep.refobjid = source_table.oid
            JOIN pg_namespace dependent_ns
                ON dependent_view.relnamespace = dependent_ns.oid
            WHERE source_table.relname = '%s';
            """,
            (IdentifierAdapter(self.name, quote=False),),
        )
        for dependent_view in self.env.cr.fetchall():
            self.logger.info(
                "Dropping view %s depends on table %s (to be dropped)",
                dependent_view[0],
                self.name,
            )
            self.env.cr.execute("DROP VIEW %s", (IdentifierAdapter(dependent_view[0]),))
            lines.filtered(lambda x, view=dependent_view[0]: x.name == view).write(
                {"purged": True}
            )
