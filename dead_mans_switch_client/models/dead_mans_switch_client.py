# -*- coding: utf-8 -*-
# © 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
import logging
import os
try:
    import psutil
except ImportError:
    psutil = None
import urllib2
from openerp.osv import orm


class DeadMansSwitchClient(orm.AbstractModel):
    _name = 'dead.mans.switch.client'
    _register = True

    def _get_data(self, cr, uid, context=None):
        ram = 0
        cpu = 0
        if psutil:
            process = psutil.Process(os.getpid())
            # psutil changed its api through versions
            processes = [process]
            if process.parent:
                if hasattr(process.parent, '__call__'):
                    process = process.parent()
                else:
                    process = process.parent
                if hasattr(process, 'children'):
                    processes += process.children(True)
                elif hasattr(process, 'get_children'):
                    processes += process.get_children(True)
            for process in processes:
                if hasattr(process, 'memory_percent'):
                    ram += process.memory_percent()
                if hasattr(process, 'cpu_percent'):
                    cpu += process.cpu_percent()
        return {
            'database_uuid': self.pool['ir.config_parameter'].get_param(
                cr, uid, 'database.uuid', context=context),
            'cpu': cpu,
            'ram': ram,
            'user_count': 0,
        }

    def alive(self, cr, uid, context=None):
        url = self.pool['ir.config_parameter'].get_param(
            cr, uid, 'dead_mans_switch_client.url')
        logger = logging.getLogger(__name__)
        if not url:
            logger.error('No server configured!')
            return
        data = self._get_data(cr, uid, context=context)
        logger.debug('sending %s', data)
        urllib2.urlopen(
            urllib2.Request(
                url,
                json.dumps({
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': data,
                }),
                {
                    'Content-Type': 'application/json',
                }))
