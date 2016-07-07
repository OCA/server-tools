# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import orm, fields
from openerp.tools.translate import _
from ..identifier_adapter import IdentifierAdapter


class CleanupPurgeLineTable(orm.TransientModel):
    _inherit = 'cleanup.purge.line'
    _name = 'cleanup.purge.line.table'

    _columns = {
        'wizard_id': fields.many2one(
            'cleanup.purge.wizard.table', 'Purge Wizard', readonly=True),
        }

    def purge(self, cr, uid, ids, context=None):
        """
        Unlink tables upon manual confirmation.
        """
        lines = self.browse(cr, uid, ids, context=context)
        tables = [line.name for line in lines]
        for line in lines:
            if line.purged:
                continue

            # Retrieve constraints on the tables to be dropped
            # This query is referenced in numerous places
            # on the Internet but credits probably go to Tom Lane
            # in this post http://www.postgresql.org/\
            # message-id/22895.1226088573@sss.pgh.pa.us
            # Only using the constraint name and the source table,
            # but I'm leaving the rest in for easier debugging
            cr.execute(
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

            for constraint in cr.fetchall():
                if constraint[3] in tables:
                    self.logger.info(
                        'Dropping constraint %s on table %s (to be dropped)',
                        constraint[0], constraint[3])
                    cr.execute(
                        "ALTER TABLE %s DROP CONSTRAINT %s", (
                            IdentifierAdapter(constraint[3]),
                            IdentifierAdapter(constraint[0]),
                        )
                    )

            self.logger.info(
                'Dropping table %s', line.name)
            cr.execute("DROP TABLE %s", (IdentifierAdapter(line.name),))
            line.write({'purged': True})
            cr.commit()
        return True


class CleanupPurgeWizardTable(orm.TransientModel):
    _inherit = 'cleanup.purge.wizard'
    _name = 'cleanup.purge.wizard.table'

    def default_get(self, cr, uid, fields, context=None):
        res = super(CleanupPurgeWizardTable, self).default_get(
            cr, uid, fields, context=context)
        if 'name' in fields:
            res['name'] = _('Purge tables')
        return res

    def find(self, cr, uid, context=None):
        """
        Search for tables that cannot be instantiated.
        Ignore views for now.
        """
        model_ids = self.pool['ir.model'].search(cr, uid, [], context=context)
        # Start out with known tables with no model
        known_tables = ['wkf_witm_trans']
        for model in self.pool['ir.model'].browse(
                cr, uid, model_ids, context=context):

            model_pool = self.pool.get(model.model)
            if not model_pool:
                continue
            known_tables.append(model_pool._table)
            known_tables += [
                column._sql_names(model_pool)[0]
                for column in model_pool._columns.values()
                if (column._type == 'many2many' and
                    hasattr(column, '_rel'))  # unstored function fields of
                                              # type m2m don't have _rel
                ]

        # Cannot pass table names as a psycopg argument
        cr.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            AND table_name NOT IN %s""", (tuple(known_tables),))

        res = [(0, 0, {'name': row[0]}) for row in cr.fetchall()]
        if not res:
            raise orm.except_orm(
                _('Nothing to do'),
                _('No orphaned tables found'))
        return res

    _columns = {
        'purge_line_ids': fields.one2many(
            'cleanup.purge.line.table',
            'wizard_id', 'Tables to purge'),
        }
