# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2016 Camptocamp SA
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


from openerp import models, fields, api


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    monitor_rpc_calls = fields.Boolean(
        "Monitor RPC calls",
        help="Enabling this setting will log information about RPC calls "
        "in Reporting / Server Monitoring / Process info. This is not enabled "
        "by default as it generates a small performance overhead."
    )

    @api.multi
    def get_default_monitor_rpc_calls(self):
        param = self.env['ir.config_parameter'].get_param(
            'server_monitoring.monitor_rpc_calls', default=False
        )
        if param:
            param = int(param)
        else:
            param = False
        return {'monitor_rpc_calls': int(param)}

    @api.multi
    def set_default_monitor_rpc_calls(self):
        for record in self:
            value = int(record.monitor_rpc_calls) or ''
            self.env['ir.config_parameter'].set_param(
                'server_monitoring.monitor_rpc_calls', value
            )
