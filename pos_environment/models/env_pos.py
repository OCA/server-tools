# -*- coding: utf-8 -*-
# Copyright 2012-2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openerp import api, fields, models

from openerp.addons.server_environment import serv_config


class PosConfig(models.Model):
    _inherit = 'pos.config'

    proxy_ip_calc = fields.Char(
        'IP Address from settings',
        size=45,
        compute='_compute_proxy_ip_server_env',
        required=False,
        readonly=True,
    )

    @api.multi
    def _compute_proxy_ip_server_env(self):
        for config in self:
            global_section_name = 'hardware_proxy'

            # default vals
            config_vals = {'proxy_ip': '', 'proxy_ip_calc': ''}
            if serv_config.has_section(global_section_name):
                config_vals.update((serv_config.items(global_section_name)))

            if config and config.name:
                custom_section_name = '.'.join((global_section_name, config.name))
                if serv_config.has_section(custom_section_name):
                    config_vals.update(serv_config.items(custom_section_name))

            config.update(config_vals)
            config.proxy_ip = config_vals['proxy_ip']

    @api.onchange('proxy_ip_calc')
    @api.depends('proxy_ip_calc')
    def _copy_value(self):
        self.proxy_ip = self.proxy_ip_calc
