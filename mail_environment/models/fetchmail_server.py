# Copyright 2012-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import operator
from odoo import api, fields, models

from odoo.addons.server_environment.models import serv_config


class FetchmailServer(models.Model):
    """Incoming POP/IMAP mail server account"""
    _inherit = 'fetchmail.server'

    server = fields.Char(compute='_compute_server_env',
                         states={})
    port = fields.Integer(compute='_compute_server_env',
                          states={})
    type = fields.Selection(compute='_compute_server_env',
                            search='_search_type',
                            states={})
    user = fields.Char(compute='_compute_server_env',
                       states={})
    password = fields.Char(compute='_compute_server_env',
                           states={})
    is_ssl = fields.Boolean(compute='_compute_server_env')
    attach = fields.Boolean(compute='_compute_server_env')
    original = fields.Boolean(compute='_compute_server_env')

    @api.depends()
    def _compute_server_env(self):
        for fetchmail in self:
            global_section_name = 'incoming_mail'

            key_types = {'port': int,
                         'is_ssl': lambda a: bool(int(a or 0)),
                         'attach': lambda a: bool(int(a or 0)),
                         'original': lambda a: bool(int(a or 0)),
                         }

            # default vals
            config_vals = {'port': 993,
                           'is_ssl': 0,
                           'attach': 0,
                           'original': 0,
                           }
            if serv_config.has_section(global_section_name):
                config_vals.update(serv_config.items(global_section_name))

            custom_section_name = '.'.join((global_section_name,
                                            fetchmail.name))
            if serv_config.has_section(custom_section_name):
                config_vals.update(serv_config.items(custom_section_name))

            for key, to_type in key_types.items():
                if config_vals.get(key):
                    config_vals[key] = to_type(config_vals[key])

            fetchmail.update(config_vals)

    @api.model
    def _search_type(self, oper, value):
        operators = {
            '=': operator.eq,
            '!=': operator.ne,
            'in': operator.contains,
            'not in': lambda a, b: not operator.contains(a, b),
        }
        if oper not in operators:
            return [('id', 'in', [])]
        servers = self.search([]).filtered(
            lambda s: operators[oper](value, s.type)
        )
        return [('id', 'in', servers.ids)]
