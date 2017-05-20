# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import datetime

from openerp import models, fields, api
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


_logger = logging.getLogger(__name__)


class ModelRowCount(models.Model):
    _name = 'server.monitor.model.row.count'

    name = fields.Char('Table name', readonly=True)
    count = fields.Bigint('Row count', readonly=True)
    measure_id = fields.Many2one('server.monitor.database',
                                 string='Measure',
                                 ondelete='cascade',
                                 readonly=True)
    timestamp = fields.Datetime(related='measure_id.name',
                                string='Timestamp',
                                type='datetime',
                                store=True)
    _order = 'timestamp DESC, count DESC'


class ModelTableSize(models.Model):
    _name = 'server.monitor.model.table.size'

    name = fields.Char('Table name', readonly=True)
    size = fields.Bigint('Size (bytes)', readonly=True)
    hsize = fields.Char('Size', readonly=True)
    measure_id = fields.Many2one('server.monitor.database',
                                 string='Measure',
                                 ondelete='cascade', readonly=True)
    timestamp = fields.Datetime(related='measure_id.name',
                                string='Timestamp',
                                store=True)

    _order = 'timestamp DESC, size DESC'


class ModelTableActivityRead(models.Model):
    _name = 'server.monitor.model.table.activity.read'
    name = fields.Char('Table name')
    disk_reads = fields.Bigint('Disk reads (heap blocks)', readonly=True)
    cache_reads = fields.Bigint('Cache reads', readonly=True)
    total_reads = fields.Bigint('Total reads', readonly=True)
    measure_id = fields.Many2one('server.monitor.database',
                                 string='Measure',
                                 ondelete='cascade', readonly=True)
    timestamp = fields.Datetime(related='measure_id.name',
                                string='Timestamp',
                                store=True)

    _order = 'timestamp DESC, total_reads DESC'


class ModelTableActivityUpdate(models.Model):
    _name = 'server.monitor.model.table.activity.update'

    name = fields.Char('Table name', readonly=True)
    seq_scan = fields.Bigint('Seq scans', readonly=True)
    idx_scan = fields.Bigint('Idx scans', readonly=True)
    lines_read_total = fields.Bigint('Tot lines read', readonly=True)
    num_insert = fields.Bigint('Inserts', readonly=True)
    num_update = fields.Bigint('Updates', readonly=True)
    num_delete = fields.Bigint('Deletes', readonly=True)
    measure_id = fields.Many2one('server.monitor.database',
                                 string='Measure',
                                 ondelete='cascade',
                                 readonly=True)
    timestamp = fields.Datetime(related='measure_id.name',
                                string='Timestamp',
                                store=True)

    _order = 'timestamp DESC, num_update DESC'


class ServerMonitorDatabase(models.Model):
    _name = 'server.monitor.database'

    @api.model
    def _model_row_count(self):
        res = []
        query = ("SELECT schemaname || '.' || relname as name, "
                 "       n_live_tup as count "
                 "FROM pg_stat_user_tables "
                 "ORDER BY n_live_tup DESC")
        self.env.cr.execute(query)
        for val in self.env.cr.dictfetchall():
            res.append((0, 0, val))
        return res

    @api.model
    def _model_table_size(self):
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
        self.env.cr.execute(query)
        for val in self.env.cr.dictfetchall():
            res.append((0, 0, val))
        return res

    @api.model
    def _model_table_activity_read(self):
        res = []
        query = ("SELECT schemaname || '.' || relname as name, "
                 "       heap_blks_read as disk_reads, "
                 "       heap_blks_hit as cache_reads, "
                 "       heap_blks_read + heap_blks_hit as total_reads "
                 "FROM pg_statio_user_tables "
                 "ORDER BY heap_blks_read + heap_blks_hit DESC"
                 )
        self.env.cr.execute(query)
        for val in self.env.cr.dictfetchall():
            res.append((0, 0, val))
        return res

    @api.model
    def _model_table_activity_update(self):
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
        self.env.cr.execute(query)
        for val in self.env.cr.dictfetchall():
            res.append((0, 0, val))
        return res

    name = fields.Datetime('Timestamp',
                           readonly=True,
                           default=fields.Datetime.now)
    info = fields.Char('Information')
    table_nb_row_ids = fields.One2many('server.monitor.model.row.count',
                                       'measure_id',
                                       'Model row counts',
                                       default=_model_row_count,
                                       readonly=True)
    table_size_ids = fields.One2many('server.monitor.model.table.size',
                                     'measure_id',
                                     'Model table size',
                                     default=_model_table_size,
                                     readonly=True)
    table_activity_read_ids = fields.One2many(
        'server.monitor.model.table.activity.read',
        'measure_id',
        'Model table read activity',
        default=_model_table_activity_read,
        readonly=True)
    table_activity_update_ids = fields.One2many(
        'server.monitor.model.table.activity.update',
        'measure_id',
        'Model table update activity',
        default=_model_table_activity_update,
        readonly=True)

    _order = 'name DESC'

    @api.model
    def log_measure(self):
        self.create({})
        return True

    @api.model
    def cleanup(self, age):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=age)
        when = (now - delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        records = self.search([('name', '<', when)])
        _logger.debug('Database monitor cleanup: removing %d records',
                      len(records))
        records.unlink()
