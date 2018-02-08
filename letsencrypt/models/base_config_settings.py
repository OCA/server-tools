# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    dns_provider = fields.Selection(
        [('shell', 'Shell')],
        string='DNS Provider',
        help='If we need to respond to a DNS challenge we need to add '
             'a TXT record on your DNS. If you leave this to Shell '
             'then you signify to the module that this will be taken '
             'care off by that script written below. '
             'Generally new modules that are made '
             'to support various VPS providers add attributes here.',
    )
    script = fields.Text(
        'Script',
        help='Write your script that will update your DNS TXT records.',
    )
    altnames = fields.Text(
        default='',
        help='Domains for which you want to include on the CSR '
             'Separate with commas.',
    )
    needs_dns_provider = fields.Boolean()
    reload_command = fields.Text(
        'Reload Command',
        help='Fill this with the command to restart your web server.',
    )

    @api.onchange('altnames')
    def onchange_altnames(self):
        if self.altnames:
            self.needs_dns_provider = any(
                '*.' in altname for altname in self.altnames.split(','))

    @api.model
    def default_get(self, field_list):
        res = super(BaseConfigSettings, self).default_get(field_list)
        ir_config_parameter = self.env['ir.config_parameter']
        res.update({
            'dns_provider': ir_config_parameter.get_param(
                'letsencrypt_dns_provider'),
            'script': ir_config_parameter.get_param(
                'letsencrypt_script'),
            'altnames': ir_config_parameter.get_param(
                'letsencrypt_altnames'),
            'reload_command': ir_config_parameter.get_param(
                'letsencrypt.reload_command'),
        })
        return res

    @api.multi
    def set_dns_provider(self):
        self.ensure_one()
        ir_config_parameter = self.env['ir.config_parameter']
        ir_config_parameter.set_param(
            'letsencrypt_dns_provider',
            self.dns_provider)
        ir_config_parameter.set_param(
            'letsencrypt_needs_dns_provider',
            self.needs_dns_provider)
        ir_config_parameter.set_param(
            'letsencrypt_script',
            self.script)
        ir_config_parameter.set_param(
            'letsencrypt_altnames',
            self.altnames)
        ir_config_parameter.set_param(
            'letsencrypt.reload_command',
            self.reload_command)
        return True
