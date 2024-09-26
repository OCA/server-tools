# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Let's Encrypt",
    "version": "10.0.2.0.1",
    "author": "Therp BV,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools"
               "/tree/10.0/letsencrypt",
    "license": "AGPL-3",
    "category": "Hidden/Dependency",
    "summary": "Request SSL certificates from letsencrypt.org",
    "depends": [
        "base_setup",
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "views/base_config_settings.xml",
    ],
    "demo": [
        "demo/ir_cron.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "external_dependencies": {
        "python": [
            "acme",
            "cryptography",
            "dns",
            "josepy",
        ],
    },
}
