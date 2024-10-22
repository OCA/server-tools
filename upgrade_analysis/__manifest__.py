# Copyright 2011-2015 Therp BV <https://therp.nl>
# Copyright 2016 Opener B.V. <https://opener.am>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Upgrade Analysis",
    "summary": "Performs a difference analysis between modules"
    " installed on two different Odoo instances",
    "version": "16.0.1.1.0",
    "category": "Migration",
    "author": "Therp BV, Opener B.V., GRAP, Odoo Community Association (OCA)",
    "maintainers": ["StefanRijnhart", "legalsylvain"],
    "website": "https://github.com/OCA/server-tools",
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/view_upgrade_comparison_config.xml",
        "views/view_upgrade_analysis.xml",
        "views/view_upgrade_record.xml",
        "wizards/view_upgrade_generate_record_wizard.xml",
        "wizards/view_upgrade_install_wizard.xml",
    ],
    "installable": True,
    "depends": ["base"],
    "external_dependencies": {
        "python": ["mako", "dataclasses", "odoorpc", "openupgradelib"],
    },
    "license": "AGPL-3",
}
