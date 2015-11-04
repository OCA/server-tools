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

from openerp.osv import osv, fields


class ir_model(osv.osv):
    _inherit = 'ir.model'

    def compute_stats(self, cr, uid, ids, field_names, arg, context=None):
        cr.execute("CREATE EXTENSION IF NOT EXISTS pgstattuple;")

        res = {}
        for model in self.browse(cr, uid, ids, context=context):
            if model.osv_memory:
                res[model.id] = {
                    'stat_table': False,
                    'stat_type': False,
                    'stat_bytes': 0,
                    'stat_count': 0,
                    'stat_count_data': 0,
                }
            else:
                pool_model = self.pool[model.model]
                cr.execute("select 'table' from pg_tables"
                           " where schemaname='public'"
                           "   and tablename='%s'"
                           " union "
                           "select 'view' from pg_views"
                           " where schemaname='public'"
                           "   and viewname='%s'"
                           ";" % (pool_model._table, pool_model._table))
                q_res = cr.fetchall()
                no_table = not q_res
                if not no_table:
                    type_table = q_res.pop()[0]
                    if type_table == 'table':
                        cr.execute(
                            "select table_len, tuple_count"
                            " from pgstattuple('%s')"
                            % pool_model._table)
                        table_len, tuple_count = cr.fetchall().pop()
                    else:
                        cr.execute(
                            "select count(*) from %s"
                            % pool_model._table)
                        table_len, tuple_count = 0, cr.fetchall().pop()[0]
                else:
                    table_len, tuple_count = 0, 0
                if tuple_count:
                    cr.execute(
                        "select count(*) from ir_model_data where model='%s'"
                        % model.model)
                    tuple_count_data = cr.fetchall().pop()[0]
                else:
                    tuple_count_data = 0
                res[model.id] = {
                    'stat_table': pool_model._table,
                    'stat_type': "no_table" if no_table else type_table,
                    'stat_bytes': 0 if no_table else table_len,
                    'stat_count': 0 if no_table else tuple_count,
                    'stat_count_data': 0 if no_table else tuple_count_data,
                }

        return res

    _columns = {
        'stat_table': fields.function(
            compute_stats,
            string="Table name",
            type="char",
            multi="stats"),
        'stat_type': fields.function(
            compute_stats,
            string="Type of table",
            type="selection",
            selection=[("no_table", "No table"),
                       ("table", "Table"),
                       ("view", "View")],
            multi="stats"),
        'stat_bytes': fields.function(
            compute_stats,
            string="Size in bytes",
            type="integer",
            multi="stats"),
        'stat_count': fields.function(
            compute_stats,
            string="Number of rows",
            type="integer",
            multi="stats"),
        'stat_count_data': fields.function(
            compute_stats,
            string="Number of data",
            type="integer",
            multi="stats"),
    }
