# -*- coding: utf-8 -*-
# © 2017 innoviù Srl <http://www.innoviu.com>
# © 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Bypass Record Rules",
    "summary": "Allows to bypass record rules",
    "version": "10.0.1.0.0",
    "category": "Hidden/Dependency",
    "website": "https://github.com/OCA/server-tools/tree/"
               "10.0/base_bypass_record_rules",
    "author": "innoviù Srl, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "depends": [
        'base',
    ],
    "data": [
        'views/ir_rule.xml',
    ],
    "installable": True,
}
