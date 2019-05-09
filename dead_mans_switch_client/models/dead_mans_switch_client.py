# © 2015-2016 Therp BV <http://therp.nl>
# © 2015 Grupo ESOC Ingeniería de Servicios, S.L.U. - Jairo Llopis
# © 2017 Avoin.Systems - Miku Laitinen
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
import logging
import os
try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None
import urllib
from odoo import api, models
from odoo.tools.config import config

SEND_TIMEOUT = 60


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
            processes = [process]
            if config.get('workers') and process.parent:  # pragma: no cover
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
                else:  # pragma: no cover
                    ram = None
                if hasattr(process, 'cpu_percent'):
                    cpu += process.cpu_percent()
                else:  # pragma: no cover
                    cpu = None
        user_count = 0
        if 'bus.presence' in self.env.registry:
            user_count = self.env['bus.presence'].search_count([
                ('status', '=', 'online'),
            ])
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
        timeout = self.env['ir.config_parameter'].get_param(
            'dead_mans_switch_client.send_timeout', SEND_TIMEOUT)
        data = self._get_data()
        logger.debug('sending %s', data)
        urllib.request.urlopen(
            urllib.request.Request(
                url=url,
                data=json.dumps({
                    'jsonrpc': '2.0',
                    'method': 'call',
                    'params': data,
                }).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                }),
            timeout=timeout)

    @api.model
    def _install_default_url(self):
        """Set up a default URL."""
        conf = self.env["ir.config_parameter"]
        name = "dead_mans_switch_client.url"
        param = conf.get_param(name)

        if not param:
            url = "{}/dead_mans_switch/alive".format(
                conf.get_param(
                    "report.url",
                    conf.get_param(
                        "web.base.url",
                        "http://localhost")))
            conf.set_param(name, url)
