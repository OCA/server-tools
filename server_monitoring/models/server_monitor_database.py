# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
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
import logging
import datetime

from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


_logger = logging.getLogger(__name__)


class ModelRowCount(orm.Model):
    _name = 'server.monitor.model.row.count'
    _columns = {
        'name': fields.text('Table name', readonly=True),
        'count': fields.bigint('row count', readonly=True),
        'measure_id': fields.many2one('server.monitor.database',
                                      'Measure',
                                      ondelete='cascade',
                                      readonly=True),
        'timestamp': fields.related('measure_id', 'name',
                                    string='timestamp',
                                    type='datetime',
                                    store=True),
        }
    _order = 'timestamp DESC, count DESC'


class ModelTableSize(orm.Model):
    _name = 'server.monitor.model.table.size'
    _columns = {
        'name': fields.text('Table name', readonly=True),
        'size': fields.bigint('Size (bytes)', readonly=True),
        'hsize': fields.text('Size', readonly=True),
        'measure_id': fields.many2one('server.monitor.database',
                                      'Measure',
                                      ondelete='cascade', readonly=True),
        'timestamp': fields.related('measure_id', 'name',
                                    string='timestamp',
                                    type='datetime',
                                    store=True),
        }
    _order = 'timestamp DESC, size DESC'


class ModelTableActivityRead(orm.Model):
    _name = 'server.monitor.model.table.activity.read'
    _columns = {
        'name': fields.text('Table name'),
        'disk_reads': fields.bigint('Disk reads (heap blocks)', readonly=True),
        'cache_reads': fields.bigint('Cache reads', readonly=True),
        'total_reads': fields.bigint('Total reads', readonly=True),
        'measure_id': fields.many2one('server.monitor.database',
                                      'Measure',
                                      ondelete='cascade', readonly=True),
        'timestamp': fields.related('measure_id', 'name',
                                    string='timestamp',
                                    type='datetime',
                                    store=True),
        }
    _order = 'timestamp DESC, total_reads DESC'


class ModelTableActivityUpdate(orm.Model):
    _name = 'server.monitor.model.table.activity.update'
    _columns = {
        'name': fields.text('Table name', readonly=True),
        'seq_scan': fields.bigint('Seq scans', readonly=True),
        'idx_scan': fields.bigint('Idx scans', readonly=True),
        'lines_read_total': fields.bigint('Tot lines read', readonly=True),
        'num_insert': fields.bigint('Inserts', readonly=True),
        'num_update': fields.bigint('Updates', readonly=True),
        'num_delete': fields.bigint('Deletes', readonly=True),
        'measure_id': fields.many2one('server.monitor.database',
                                      'Measure',
                                      ondelete='cascade',
                                      readonly=True),
        'timestamp': fields.related('measure_id', 'name',
                                    string='timestamp',
                                    type='datetime',
                                    store=True),
        }
    _order = 'timestamp DESC, num_update DESC'


class ServerMonitorDatabase(orm.Model):
    _name = 'server.monitor.database'
    _columns = {
        'name': fields.datetime('Timestamp', readonly=True),
        'info': fields.text('Information'),
        'table_nb_row_ids': fields.one2many('server.monitor.model.row.count',
                                            'measure_id',
                                            'Model row counts',
                                            readonly=True),
        'table_size_ids': fields.one2many('server.monitor.model.table.size',
                                          'measure_id',
                                          'Model table size',
                                          readonly=True),
        'table_activity_read_ids': fields.one2many(
            'server.monitor.model.table.activity.read',
            'measure_id',
            'Model table read activity',
            readonly=True),
        'table_activity_update_ids': fields.one2many(
            'server.monitor.model.table.activity.update',
            'measure_id',
            'Model table update activity',
            readonly=True),
        }
    _order = 'name DESC'

    def _model_row_count(self, cr, uid, context):
        res = []
        query = ("SELECT schemaname || '.' || relname as name, "
                 "       n_live_tup as count "
                 "FROM pg_stat_user_tables "
                 "ORDER BY n_live_tup DESC")
        cr.execute(query)
        for val in cr.dictfetchall():
            res.append((0, 0, val))
        return res

    def _model_table_size(self, cr, uid, context):
        res = []
        query = (
            "SELECT nspname || '.' || relname AS name, "
            "        pg_size_pretty(pg_total_relation_size(C.oid)) AS hsize, "
            "        pg_total_relation_size(C.oid) AS size "
            "FROM pg_class C LEFT JOIN pg_namespace N "
            "              ON (N.oid = C.relnamespace) "
            "WHERE nspname NOT IN ('pg_catalog', 'information_schema') "
            "  AND C.relkind <> 'i' "
            "  AND nspname !~ '^pg_toast' "
            "ORDER BY pg_total_relation_size(C.oid) DESC"
            )
        cr.execute(query)
        for val in cr.dictfetchall():
            res.append((0, 0, val))
        return res

    def _model_table_activity_read(self, cr, uid, context):
        res = []
        query = ("SELECT schemaname || '.' || relname as name, "
                 "       heap_blks_read as disk_reads, "
                 "       heap_blks_hit as cache_reads, "
                 "       heap_blks_read + heap_blks_hit as total_reads "
                 "FROM pg_statio_user_tables "
                 "ORDER BY heap_blks_read + heap_blks_hit DESC"
                 )
        cr.execute(query)
        for val in cr.dictfetchall():
            res.append((0, 0, val))
        return res

    def _model_table_activity_update(self, cr, uid, context):
        res = []
        query = ("SELECT schemaname || '.' || relname as name, "
                 "       seq_scan, "
                 "       idx_scan, "
                 "       idx_tup_fetch + seq_tup_read as lines_read_total, "
                 "       n_tup_ins as num_insert, "
                 "       n_tup_upd as num_update, "
                 "       n_tup_del as num_delete "
                 "FROM pg_stat_user_tables "
                 "ORDER BY n_tup_upd + n_tup_ins + n_tup_del desc")
        cr.execute(query)
        for val in cr.dictfetchall():
            res.append((0, 0, val))
        return res

    _defaults = {
        'name': fields.datetime.now,
        'table_nb_row_ids': _model_row_count,
        'table_size_ids': _model_table_size,
        'table_activity_read_ids': _model_table_activity_read,
        'table_activity_update_ids': _model_table_activity_update,
        }

    def log_measure(self, cr, uid, context=None):
        fields = self._defaults.keys()
        defaults = self.default_get(cr, uid, fields, context=context)
        self.create(cr, uid, defaults, context=context)
        return True

    def cleanup(self, cr, uid, age, context=None):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=age)
        when = (now - delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        ids = self.search(cr, uid,
                          [('name', '<', when)],
                          context=context)
        _logger.debug('Database monitor cleanup: removing %d records',
                      len(ids))
        self.unlink(cr, uid, ids, context=context)
