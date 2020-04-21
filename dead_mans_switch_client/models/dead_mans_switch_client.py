# © 2015-2020 Therp BV <http://therp.nl>
# © 2015 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# © 2017 Avoin.Systems - Miku Laitinen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import os

import psutil
import requests

from odoo import api, models
from odoo.tools import config

_logger = logging.getLogger(__name__)

SEND_TIMEOUT = 60


class DeadMansSwitchClient(models.AbstractModel):
    _name = 'dead.mans.switch.client'
    _description = "Dead man's switch client"
    _register = True

    @api.model
    def _get_data(self):
        process = psutil.Process(os.getpid())
        processes = [process]
        if config.get('workers'):  # pragma: no cover
            process = process.parent()
            processes = process.children(recursive=True)
        ram = 0
        cpu = 0
        for process in processes:
            ram += process.memory_percent()
            cpu += process.cpu_percent()
        user_count = 0
        if 'bus.presence' in self.env.registry:
            user_count = self.env['bus.presence'].search_count([
                ('status', '=', 'online'),
            ])
        dbuuid = self.env["ir.config_parameter"].get_param("database.uuid")
        return {
            'database_uuid': dbuuid,
            'cpu': cpu,
            'ram': ram,
            'user_count': user_count,
        }

    @api.model
    def alive(self):
        url = self.env['ir.config_parameter'].get_param(
            'dead_mans_switch_client.url')
        if not url:
            _logger.error('No server configured!')
            return
        timeout = self.env['ir.config_parameter'].get_param(
            'dead_mans_switch_client.send_timeout', SEND_TIMEOUT)
        data = self._get_data()
        _logger.debug('Sending %r', data)
        requests.post(
            url,
            json={
                'jsonrpc': '2.0',
                'method': 'call',
                'params': data,
            },
            headers={
                'Content-Type': 'application/json',
            },
            timeout=timeout,
        )
