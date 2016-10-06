# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Let's encrypt",
    "version": "9.0.1.0.0",
    "author": "Therp BV,"
              "Tecnativa,"
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Hidden/Dependency",
    "summary": "Request SSL certificates from letsencrypt.org",
    "depends": [
        'base',
    ],
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "demo/ir_cron.xml",
    ],
    "post_init_hook": 'post_init_hook',
    'installable': False,
    "external_dependencies": {
        'bin': [
            'openssl',
        ],
        'python': [
            'acme_tiny',
            'IPy',
        ],
    },
}
