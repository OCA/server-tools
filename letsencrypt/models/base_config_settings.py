# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, exceptions, fields, models


DNS_SCRIPT_DEFAULT = """# Write your script here
# It should create a TXT record of $LETSENCRYPT_DNS_CHALLENGE
# on _acme-challenge.$LETSENCRYPT_DNS_DOMAIN
"""


class BaseConfigSettings(models.TransientModel):
    _inherit = 'base.config.settings'

    letsencrypt_altnames = fields.Text(
        string="Domain names",
        default='',
        help=(
            'Additional domains to include on the CSR. '
            'Separate with commas or newlines.'
        ),
    )
    letsencrypt_dns_provider = fields.Selection(
        selection=[('shell', 'Shell script')],
        string='DNS provider',
        help=(
            'For wildcard certificates we need to add a TXT record on your '
            'DNS. If you set this to "Shell script" you can enter a shell '
            'script. Other options can be added by installing additional '
            'modules.'
        ),
    )
    letsencrypt_dns_shell_script = fields.Text(
        string='DNS update script',
        help=(
            'Write a shell script that will update your DNS TXT records. '
            'You can use the $LETSENCRYPT_DNS_CHALLENGE and '
            '$LETSENCRYPT_DNS_DOMAIN variables.'
        ),
        default=DNS_SCRIPT_DEFAULT,
    )
    letsencrypt_needs_dns_provider = fields.Boolean()
    letsencrypt_reload_command = fields.Text(
        string='Server reload command',
        help='Fill this with the command to restart your web server.',
    )
    letsencrypt_testing_mode = fields.Boolean(
        string='Use testing server',
        help=(
            "Use the Let's Encrypt staging server, which has higher rate "
            "limits but doesn't create valid certificates."
        ),
    )
    letsencrypt_prefer_dns = fields.Boolean(
        string="Prefer DNS validation",
        help=(
            "Validate through DNS even when HTTP validation is possible. "
            "Use this if your Odoo instance isn't publicly accessible."
        ),
    )

    @api.onchange('letsencrypt_altnames', 'letsencrypt_prefer_dns')
    def letsencrypt_check_dns_required(self):
        altnames = self.letsencrypt_altnames or ''
        self.letsencrypt_needs_dns_provider = (
            "*." in altnames or self.letsencrypt_prefer_dns
        )

    @api.model
    def default_get(self, fields_list):
        res = super(BaseConfigSettings, self).default_get(fields_list)
        get_param = self.env['ir.config_parameter'].get_param
        res.update(
            {
                'letsencrypt_dns_provider': get_param(
                    'letsencrypt.dns_provider'
                ),
                'letsencrypt_dns_shell_script': get_param(
                    'letsencrypt.dns_shell_script', DNS_SCRIPT_DEFAULT
                ),
                'letsencrypt_altnames': get_param('letsencrypt.altnames', ''),
                'letsencrypt_reload_command': get_param(
                    'letsencrypt.reload_command'
                ),
                'letsencrypt_needs_dns_provider': (
                    '*.' in get_param('letsencrypt.altnames', '')
                ),
                'letsencrypt_testing_mode': (
                    get_param('letsencrypt.testing_mode', 'False') == 'True'
                ),
                'letsencrypt_prefer_dns': (
                    get_param('letsencrypt.prefer_dns', 'False') == 'True'
                ),
            }
        )
        return res

    @api.multi
    def set_letsencrypt_settings(self):
        self.ensure_one()
        self.letsencrypt_check_dns_required()

        if self.letsencrypt_dns_provider == 'shell':
            lines = [
                line.strip()
                for line in self.letsencrypt_dns_shell_script.split('\n')
            ]
            if all(line == '' or line.startswith('#') for line in lines):
                raise exceptions.ValidationError(
                    "You didn't write a DNS update script!"
                )

        set_param = self.env['ir.config_parameter'].set_param
        set_param('letsencrypt.dns_provider', self.letsencrypt_dns_provider)
        set_param(
            'letsencrypt.dns_shell_script', self.letsencrypt_dns_shell_script
        )
        set_param('letsencrypt.altnames', self.letsencrypt_altnames)
        set_param(
            'letsencrypt.reload_command', self.letsencrypt_reload_command
        )
        set_param(
            'letsencrypt.testing_mode',
            'True' if self.letsencrypt_testing_mode else 'False',
        )
        set_param(
            'letsencrypt.prefer_dns',
            'True' if self.letsencrypt_prefer_dns else 'False',
        )
        return True
