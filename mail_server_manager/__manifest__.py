# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Mail Server Manager",
    "version": "19.0.7.0.0",
    "category": "Technical",
    "summary": "Manage email accounts on docker-mailserver from Odoo",
    "author": "Odoo Community Association (OCA), KHALID SAHIH, Sudo System",
    "website": "https://github.com/OCA/server-tools",
    "maintainer": "khalid.sahih@sudosystem.com",
    "depends": ["mail", "base_setup"],
    # Note: fetchmail is optional - install it for IMAP support
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rules.xml",
        "data/ir_config_parameter.xml",
        "wizards/password_wizard_views.xml",
        "wizards/change_password_wizard_views.xml",
        "views/mail_account_views.xml",
        "views/res_users_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "LGPL-3",
}
