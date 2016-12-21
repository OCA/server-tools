# -*- coding: utf-8 -*-
# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models

from odoo.addons.server_environment import serv_config


class IrMailServer(models.Model):
    _inherit = "ir.mail_server"

    smtp_host = fields.Char(compute='_compute_server_env',
                            required=False,
                            readonly=True)
    smtp_port = fields.Integer(compute='_compute_server_env',
                               required=False,
                               readonly=True)
    smtp_user = fields.Char(compute='_compute_server_env',
                            required=False,
                            readonly=True)
    smtp_pass = fields.Char(compute='_compute_server_env',
                            required=False,
                            readonly=True)
    smtp_encryption = fields.Selection(compute='_compute_server_env',
                                       required=False,
                                       readonly=True)

    @api.depends()
    def _compute_server_env(self):
        for server in self:
            global_section_name = 'outgoing_mail'

            # default vals
            config_vals = {'smtp_port': 587}
            if serv_config.has_section(global_section_name):
                config_vals.update((serv_config.items(global_section_name)))

            custom_section_name = '.'.join((global_section_name, server.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            if config_vals.get('smtp_port'):
                config_vals['smtp_port'] = int(config_vals['smtp_port'])

            server.update(config_vals)
