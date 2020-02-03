# Copyright 2016-2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Let's encrypt",
    "version": "12.0.1.0.0",
    "author": "Therp BV,"
              "Tecnativa,"
              "Acysos S.L,"
              "Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/server-tools/",
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
    'installable': True,
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
