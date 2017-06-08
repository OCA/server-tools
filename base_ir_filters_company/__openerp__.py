# -*- coding: utf-8 -*-
# © 2016  Laetitia Gangloff, Acsone SA/NV (http://www.acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Filters by company",
    "version": "8.0.1.0.0",
    "author": "Acsone SA/NV,Odoo Community Association (OCA)",
    "category": "Hidden/Dependency",
    "website": "http://www.acsone.eu",
    "depends": [
        'base',
    ],
    "data": [
        "views/ir_filters.xml",
        "security/base_ir_filters_company_security.xml",
    ],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    'post_init_hook': 'set_company_to_null',
}
