# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import psutil
import requests
import os
from odoo import _, api, fields, models
from odoo.exceptions import Warning
from odoo.tools.config import config


class NagiosServer(models.Model):
    _name = 'nagios.server'
    _description = 'Nagios server'

    name = fields.Char(required=True, index=True, )
    description = fields.Text()
    target = fields.Char(
        'Nagios server',
        required=True,
    )
    requires_authentication = fields.Boolean(default=False, required=True, )
    performance_type = fields.Selection([
        ('standard', 'Standard')
    ], default='standard', required=True,
    )
    # Type should be used in order to specify information to send
    authentication_user = fields.Char()
    authentication_password = fields.Char()
    host = fields.Char(
        help='Odoo server in nagios',
        required=True,
    )
    service = fields.Char(
        help='Odoo service in nagios',
        required=True,
    )

    @api.multi
    def send(self):
        self.ensure_one()
        return self._send()

    def _send(self):
        data = self._get_nagios_data()
        performance = data['performance']
        auth = False
        if self.requires_authentication:
            auth = (self.authentication_user, self.authentication_password)
        request = requests.post(self.target, {
            'cmd_typ': 30,
            'cmd_mod': 2,
            'host': self.host,
            'service': self.service,
            'plugin_state': data['status_code'],
            'plugin_output': data['status'],
            'performance_data': ''.join(
                ["%s=%s%s;%s;%s;%s;%s" % (
                    key,
                    performance[key]['value'],
                    performance[key].get('uom', ''),
                    performance[key].get('warn', ''),
                    performance[key].get('crit', ''),
                    performance[key].get('min', ''),
                    performance[key].get('max', ''),
                ) for key in sorted(performance)])
        }, auth=auth)
        if not request.ok:
            raise Warning(_('Host %s cannot be reached') % self.target)

    def _get_nagios_data(self):
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
                if hasattr(process, 'cpu_percent'):
                    cpu += process.cpu_percent(interval=1)
        user_count = 0
        if 'bus.presence' in self.env.registry:
            user_count = self.env['bus.presence'].search_count([
                ('status', '=', 'online'),
            ])
        return {
            'status_code': 0,
            'status': 'OK',
            'performance': {
                'cpu': {
                    'value': cpu,
                },
                'ram': {
                    'value': ram,
                },
                'user_count': {
                    'value': user_count,
                },
            }
        }

    @api.model
    def _cron_send(self, domain):
        for server in self.search(domain):
            server._send()
