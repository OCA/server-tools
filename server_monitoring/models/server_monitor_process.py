# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Monitor Odoo instance.

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

import logging
import gc
from operator import itemgetter
import types
import os
import threading
import datetime
import resource

import psutil

import openerp
from openerp.http import request
from openerp import models, fields, api
from openerp import pooler
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

_monkey_patched = False


class ClassInstanceCount(models.Model):
    _name = 'server.monitor.class.instance.count'

    name = fields.Char('Class name', readonly=True)
    count = fields.Bigint('Instance count', readonly=True)
    measure_id = fields.Many2one('server.monitor.process',
                                 'Measure',
                                 readonly=True,
                                 ondelete='cascade')


def _monkey_patch_object_proxy_execute():
    orig_execute_cr = openerp.service.model.execute_cr

    def execute_cr(cr, uid, obj, method, *args, **kw):
        result = orig_execute_cr(cr, uid, obj, method, *args, **kw)
        pool = pooler.get_pool(cr.dbname)
        monitor_obj = pool.get('server.monitor.process')
        monitor = pool['ir.config_parameter'].get_param(
            cr, uid,
            'server_monitoring.monitor_rpc_calls', default=False
        )
        if monitor_obj is not None and bool(monitor):
            monitor_obj.log_measure(cr, uid, obj, method, 'xmlrpc call',
                                    False, False, context={})
        return result

    openerp.service.model.execute_cr = execute_cr


def _monkey_patch_controller_call_kw():
    orig_call_kw = openerp.addons.web.controllers.main.DataSet._call_kw

    def _call_kw(self, model, method, args, kwargs):
        result = orig_call_kw(self, model, method, args, kwargs)
        monitor_obj = request.registry.get('server.monitor.process')
        monitor = request.registry['ir.config_parameter'].get_param(
            request.cr, request.uid,
            'server_monitoring.monitor_rpc_calls', default=False
        )
        if monitor_obj is not None and bool(monitor):
            monitor_obj.log_measure(request.cr, request.uid, model, method,
                                    'jsonrpc call',
                                    False, False, context={})
        return result

    openerp.addons.web.controllers.main.DataSet._call_kw = _call_kw


class ServerMonitorProcess(models.Model):
    def __init__(self, pool, cr):
        super(ServerMonitorProcess, self).__init__(pool, cr)

    _name = 'server.monitor.process'

    def _register_hook(self, cr):
        global _monkey_patched
        if _monkey_patched:
            return
        _monkey_patched = True
        _monkey_patch_controller_call_kw()
        _monkey_patch_object_proxy_execute()

    @api.model
    def _default_pid(self):
        return os.getpid()

    @api.model
    def _default_cpu_time(self):
        r = resource.getrusage(resource.RUSAGE_SELF)
        cpu_time = r.ru_utime + r.ru_stime
        return cpu_time

    @api.model
    def _default_memory(self):
        try:
            rss, vms = psutil.Process(os.getpid()).get_memory_info()
        except AttributeError:
            # happens on travis
            vms = 0
        return vms

    @api.model
    def _default_uid(self):
        return self.env.uid

    @api.model
    def _default_thread(self):
        return threading.current_thread().name

    @api.model
    def _class_count(self):
        counts = {}
        context = self.env.context
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
                    _logger.warning('Unknown object type for %r (%s)',
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

    name = fields.Datetime('Timestamp',
                           default=fields.Datetime.now,
                           readonly=True)
    pid = fields.Integer('Process ID',
                         default=_default_pid,
                         readonly=True,
                         group_operator='count')
    thread = fields.Char('Thread ID',
                         default=_default_thread,
                         readonly=True)
    cpu_time = fields.Float(
        'CPU time',
        readonly=True,
        default=_default_cpu_time,
        group_operator='max',
        help='CPU time consumed by the current server process')
    memory = fields.Float(
        'Memory',
        default=_default_memory,
        readonly=True,
        group_operator='max',
        help='Memory consumed by the current server process')
    uid = fields.Many2one('res.users', 'User',
                          default=_default_uid,
                          readonly=True,
                          select=True)
    model = fields.Many2one('ir.model', 'Model',
                            readonly=True,
                            select=True)
    method = fields.Char('Method', readonly=True)
    status = fields.Char('RPC status', readonly=True)
    sessionid = fields.Char('Session ID', readonly=True)
    info = fields.Char('Information')
    class_count_ids = fields.One2many(
        'server.monitor.class.instance.count',
        'measure_id',
        'Class counts',
        default=_class_count,
        readonly=True)

    _order = 'name DESC'

    @api.model
    def log_measure(self, model_name, method_name, info,
                    with_class_count=True,
                    gc_collect=True):
        self_ctx = self.with_context(_x_no_class_count=not with_class_count,
                                     _x_no_gc_collect=not gc_collect)
        model_obj = self.env['ir.model']
        model = model_obj.search([('name', '=', model_name)], limit=1)
        values = {'model': model.id,
                  'method': method_name,
                  'info': info,
                  }
        record = self_ctx.sudo().create(values)
        return record

    @api.model
    def cleanup(self, age):
        now = datetime.datetime.now()
        delta = datetime.timedelta(days=age)
        when = (now - delta).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        records = self.search([('name', '<', when)])
        _logger.debug('Process monitor cleanup: removing %d records',
                      len(records))
        records.unlink()
