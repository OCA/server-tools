# -*- coding: utf-8 -*-
# Copyright 2016 Pierre Verkest <pverkest@anybox.fr>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Materialized Sql View',
    'version': '8.0.1.0.1',
    'category': 'Tools',
    'author': 'Pierre Verkest,Odoo Community Association (OCA)',
    'maintainer': 'Odoo Community Association (OCA)',
    'depends': [
        'base',
        'web',
    ],
    'demo_xml': [
    ],
    'data': [
        'security/security_group.xml',
        'security/ir.model.access.csv',
        'views/materialized_sql_view.xml',
        'menus/menus.xml',
    ],
    'js': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
}
