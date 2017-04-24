# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Module Uninstall Check",
    "summary": "Add Extra Checks before uninstallation of modules",
    "version": "8.0.1.0.0",
    "category": "Base",
    "website": "https://odoo-community.org/",
    "author": "GRAP, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        'base',
    ],
    "data": [
        'wizards/wizard_module_uninstall.xml',
        'wizards/action.xml',
        'views/ir_module_module.xml',
    ],
    "demo": [
        'demo/res_groups.xml',
    ],
}
