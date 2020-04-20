# Copyright 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# pylint: disable=consider-merging-classes-inherited
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from ..identifier_adapter import IdentifierAdapter


class CleanupPurgeLineTable(models.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.table'
    _description = 'Purge tables wizard lines'

    wizard_id = fields.Many2one(
        'cleanup.purge.wizard.table', 'Purge Wizard', readonly=True)

    @api.multi
    def purge(self):
        """
        Unlink tables upon manual confirmation.
        """
        if self:
            objs = self
        else:
            objs = self.env['cleanup.purge.line.table']\
                .browse(self._context.get('active_ids'))
        tables = objs.mapped('name')
        no_retries = 10
        retry = 0
        retry_objs = self.env['cleanup.purge.line.table']
        while objs and retry < no_retries:
            retry += 1
            for line in objs:
                if line.purged:
                    continue
                self.env.cr.execute("""
                    SELECT count(0)
                    FROM pg_depend
                        JOIN pg_rewrite ON pg_depend.objid = pg_rewrite.oid
                        JOIN pg_class as dependent_view
                        ON pg_rewrite.ev_class = dependent_view.oid
                        JOIN pg_class as source_table
                        ON pg_depend.refobjid = source_table.oid
                        JOIN pg_attribute
                        ON pg_depend.refobjid = pg_attribute.attrelid
                        AND pg_depend.refobjsubid = pg_attribute.attnum
                        JOIN pg_namespace dependent_ns
                        ON dependent_ns.oid = dependent_view.relnamespace
                        JOIN pg_namespace source_ns
                        ON source_ns.oid = source_table.relnamespace
                    WHERE
                        source_ns.nspname = 'public'
                        AND source_table.relname = '%s'
                        AND pg_attribute.attnum > 0
                        AND pg_attribute.attname = 'id';
                """, (IdentifierAdapter(line.name, quote=False),))
                relations = self.env.cr.fetchone()[0]
                self.env.cr.execute("""
                    select count(R.TABLE_NAME)
                    from INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE u
                        inner join INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS FK
                         on U.CONSTRAINT_CATALOG = FK.UNIQUE_CONSTRAINT_CATALOG
                         and U.CONSTRAINT_SCHEMA = FK.UNIQUE_CONSTRAINT_SCHEMA
                         and U.CONSTRAINT_NAME = FK.UNIQUE_CONSTRAINT_NAME
                        inner join INFORMATION_SCHEMA.KEY_COLUMN_USAGE R
                         ON R.CONSTRAINT_CATALOG = FK.CONSTRAINT_CATALOG
                         AND R.CONSTRAINT_SCHEMA = FK.CONSTRAINT_SCHEMA
                         AND R.CONSTRAINT_NAME = FK.CONSTRAINT_NAME
                    WHERE U.COLUMN_NAME = 'id'
                        AND U.TABLE_NAME = '%s';
                """, (IdentifierAdapter(line.name, quote=False),))
                relations += self.env.cr.fetchone()[0]
                # TODO: to take into account non-relational fields (i.e. properties)
                if not relations:
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
                        """, (IdentifierAdapter(line.name, quote=False),))

                    for constraint in self.env.cr.fetchall():
                        if constraint[3] in tables:
                            self.logger.info(
                                'Dropping constraint %s on table %s (to be dropped)',
                                constraint[0], constraint[3])
                            self.env.cr.execute(
                                "ALTER TABLE %s DROP CONSTRAINT %s",
                                (
                                    IdentifierAdapter(constraint[3]),
                                    IdentifierAdapter(constraint[0])
                                ))

                    self.logger.info(
                        'Dropping table %s', line.name)
                    self.env.cr.execute(
                        "DROP TABLE %s", (IdentifierAdapter(line.name),))
                    line.write({'purged': True})
                else:
                    retry_objs |= line
            self._cr.commit()
            if len(objs) > len(retry_objs):
                objs = retry_objs
                retry_objs = self.env['cleanup.purge.line.table']
            else:
                break
        return True


class CleanupPurgeWizardTable(models.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.table'
    _description = 'Purge tables'

    @api.model
    def find(self):
        """
        Search for tables that cannot be instantiated.
        Ignore views for now.
        """
        known_tables = []
        for model in self.env['ir.model'].search([]):
            if model.model not in self.env:
                continue
            model_pool = self.env[model.model]
            known_tables.append(model_pool._table)
            known_tables += [
                column.relation
                for column in model_pool._fields.values()
                if column.type == 'many2many' and
                (column.compute is None or column.store)
                and column.relation
            ]

        self.env.cr.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            AND table_name NOT IN %s""", (tuple(known_tables),))

        res = [(0, 0, {'name': row[0]}) for row in self.env.cr.fetchall()]
        if not res:
            raise UserError(_('No orphaned tables found'))
        return res

    purge_line_ids = fields.One2many(
        'cleanup.purge.line.table', 'wizard_id', 'Tables to purge')
