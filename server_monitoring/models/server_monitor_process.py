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

"""
Monitor openerp instance.

The measures are stored in database.
cleanup cron (2 different for db and process monitoring)

* database monitoring:
  cron for capturing data
  add timestamp

* process monitoring

  TODO: log process start / end
  cron log
  RPC request log

"""
from __future__ import absolute_import

import logging
import gc
from operator import itemgetter
import types
import os
import threading
import datetime
import resource
import psutil

from openerp.osv import orm, fields, osv
from openerp import pooler
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)

BLACKLIST = (
    type, tuple, dict, list, set, frozenset,
    property,
    classmethod,
    staticmethod,
    types.FunctionType,
    types.ClassType,
    types.ModuleType, types.FunctionType, types.MethodType,
    types.MemberDescriptorType, types.GetSetDescriptorType,
    )


class ClassInstanceCount(orm.Model):
    _name = 'server.monitor.class.instance.count'
    _columns = {
        'name': fields.text('Class name', readonly=True),
        'count': fields.bigint('Instance count', readonly=True),
        'measure_id': fields.many2one('server.monitor.process',
                                      'Measure',
                                      readonly=True,
                                      ondelete='cascade'),
        }


def _monkey_patch_object_proxy_execute():
    orig_execute_cr = osv.object_proxy.execute_cr

    def execute_cr(self, cr, uid, obj, method, *args, **kw):
        result = orig_execute_cr(self, cr, uid, obj, method, *args, **kw)
        monitor_obj = pooler.get_pool(cr.dbname)['server.monitor.process']
        context = {}
        monitor_obj.log_measure(cr, uid, obj, method, 'rpc call',
                                False, False, context)
        return result

    osv.object_proxy.execute_cr = execute_cr


class ServerMonitorProcess(orm.Model):
    def __init__(self, pool, cr):
        super(ServerMonitorProcess, self).__init__(pool, cr)
        _monkey_patch_object_proxy_execute()

    _name = 'server.monitor.process'
    _columns = {
        'name': fields.datetime('Timestamp', readonly=True),
        'pid': fields.integer('Process ID', readonly=True,
                              group_operator='count'),
        'thread': fields.text('Thread ID', readonly=True),
        'cpu_time': fields.float(
            'CPU time', readonly=True,
            group_operator='max',
            help='CPU time consumed by the current server process'),
        'memory': fields.float(
            'Memory', readonly=True,
            group_operator='max',
            help='Memory consumed by the current server process'),
        'uid': fields.many2one('res.users', 'User',
                               readonly=True,
                               select=True),
        'model': fields.many2one('ir.model', 'Model',
                                 readonly=True,
                                 select=True),
        'method': fields.text('Method', readonly=True),
        'status': fields.text('RPC status', readonly=True),
        'sessionid': fields.text('Session ID', readonly=True),
        'info': fields.text('Information'),
        'class_count_ids': fields.one2many(
            'server.monitor.class.instance.count',
            'measure_id',
            'Class counts',
            readonly=True),
        }
    _order = 'name DESC'

    def _default_pid(self, cr, uid, context):
        return os.getpid()

    def _default_cpu_time(self, cr, uid, context):
        r = resource.getrusage(resource.RUSAGE_SELF)
        cpu_time = r.ru_utime + r.ru_stime
        return cpu_time

    def _default_memory(self, cr, uid, context):
        try:
            rss, vms = psutil.Process(os.getpid()).get_memory_info()
        except AttributeError:
            # happens on travis
            vms = 0
        return vms

    def _default_uid(self, cr, uid, context):
        return uid

    def _default_thread(self, cr, uid, context):
        return threading.current_thread().name

    def _class_count(self, cr, uid, context):
        counts = {}
        if context.get('_x_no_class_count'):
            return []
        if context.get('_x_no_gc_collect'):
            gc.collect()
            gc.collect()
        for obj in gc.get_objects():
            if isinstance(obj, BLACKLIST):
                continue
            try:
                cls = obj.__class__
            except:
                if isinstance(obj, types.ClassType):
                    cls = types.ClassType
                else:
                    _logger.warning('unknown object type for %r (%s)',
                                    obj, type(obj))
                    continue
            name = '%s.%s' % (cls.__module__, cls.__name__)
            try:
                counts[name] += 1
            except KeyError:
                counts[name] = 1
        info = []
        for name, count in sorted(counts.items(),
                                  key=itemgetter(1),
                                  reverse=True):
            if count < 2:
                break
            info.append({'name': name,  'count': count})
        return [(0, 0, val) for val in info]

    _defaults = {
        'name': fields.datetime.now,
        'class_count_ids': _class_count,
        'pid': _default_pid,
        'cpu_time': _default_cpu_time,
        'memory': _default_memory,
        'uid': _default_uid,
        'thread': _default_thread,
        }

    def log_measure(self, cr, uid,
                    model_name, method_name, info,
                    with_class_count=True,
                    gc_collect=True,
                    context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({
            '_x_no_class_count': not with_class_count,
            '_x_no_gc_collect': not gc_collect,
            })
        fields = self._defaults.keys()
        defaults = self.default_get(cr, uid, fields, context=ctx)
        model_obj = self.pool['ir.model']
        model_id = model_obj.search(cr, uid,
                                    [('name', '=', model_name)],
                                    context=context)
        if model_id:
            model_id = model_id[0]
        else:
            model_id = 0
        values = {'model': model_id,
                  'method': method_name,
                  'info': info,
                  }
        defaults.update(values)

        id = self.create(cr, SUPERUSER_ID, defaults, context=context)
        return id

    def cleanup(self, cr, uid, age, context=None):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=age)
        when = (now - delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        ids = self.search(cr, uid,
                          [('name', '<', when)],
                          context=context)
        _logger.debug('Process monitor cleanup: removing %d records', len(ids))
        self.unlink(cr, uid, ids, context=context)
