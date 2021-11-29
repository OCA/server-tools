# Copyright (C) 2019-Today: GRAP (<http://www.grap.coop/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Module Analysis",
    "summary": "Add analysis tools regarding installed modules"
    " to know which installed modules comes from Odoo Core, OCA, or are"
    " custom modules",
    "author": "GRAP, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/server-tools",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/view_ir_module_author.xml",
        "views/view_ir_module_type.xml",
        "views/view_ir_module_type_rule.xml",
        "views/view_ir_module_module.xml",
        "data/ir_cron.xml",
        "data/ir_config_parameter.xml",
        "data/ir_module_type.xml",
        "data/ir_module_type_rule.xml",
        "data/ir_cron.xml",
    ],
    "external_dependencies": {
        "python": ["pygount"],
    },
    "installable": True,
}
