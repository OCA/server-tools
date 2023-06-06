# 2016-2020 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Let's Encrypt",
    "version": "13.0.1.1.0",
    "author": "Therp BV," "Tecnativa," "Acysos S.L," "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Hidden/Dependency",
    "summary": "Request SSL certificates from letsencrypt.org",
    "website": "https://github.com/OCA/server-tools",
    "depends": ["base_setup"],
    "data": [
        "data/ir_config_parameter.xml",
        "data/ir_cron.xml",
        "views/res_config_settings.xml",
    ],
    "demo": ["demo/ir_cron.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "external_dependencies": {
        "python": ["acme", "cryptography", "dnspython", "josepy", "pyOpenSSL<23"]
    },
}
