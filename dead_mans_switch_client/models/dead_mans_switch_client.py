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
from openerp import api, models


class DeadMansSwitchClient(models.AbstractModel):
    _name = 'dead.mans.switch.client'
    _register = True

    @api.model
    def _get_data(self):
        ram = 0
        cpu = 0
        if psutil:
            process = psutil.Process(os.getpid())
            # psutil changed its api through versions
            if process.parent:
                if hasattr(process.parent, '__call__'):
                    process = process.parent()
                else:
                    process = process.parent
            if hasattr(process, 'memory_percent'):
                ram = process.memory_percent()
            if hasattr(process, 'cpu_percent'):
                cpu = process.cpu_percent()
        user_count = 0
        if 'im_chat.presence' in self.env.registry:
            user_count = len(self.env['im_chat.presence'].search([
                ('status', '!=', 'offline'),
            ]))
        return {
            'database_uuid': self.env['ir.config_parameter'].get_param(
                'database.uuid'),
            'cpu': cpu,
            'ram': ram,
            'user_count': user_count,
        }

    @api.model
    def alive(self):
        url = self.env['ir.config_parameter'].get_param(
            'dead_mans_switch_client.url')
        logger = logging.getLogger(__name__)
        if not url:
            logger.error('No server configured!')
            return
        data = self._get_data()
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
