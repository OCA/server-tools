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
        for line in lines:
            if line.purged:
                continue

            self.logger.info(
                'Dropping table %s and all dependent objects', line.name)
            cr.execute("DROP TABLE \"%s\" CASCADE" % (line.name,))
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
        known_tables_repr = ",".join(
            [("'%s'" % table) for table in known_tables])
        cr.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            AND table_name NOT IN (%s)""" % known_tables_repr)

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
