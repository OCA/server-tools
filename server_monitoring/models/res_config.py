# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


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
