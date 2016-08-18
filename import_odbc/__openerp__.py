# -*- coding: utf-8 -*-
# Copyright (C) 2011 - TODAY Daniel Reis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Import data from SQL and ODBC data sources.',
    'version': '1.3',
    'category': 'Tools',
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'http://launchpad.net/addons-tko',
    'license': 'AGPL-3',
    'images': [
        'images/snapshot1.png',
        'images/snapshot2.png',
    ],
    'depends': [
        'base',
        'base_external_dbsource',
    ],
    'data': [
        'import_odbc_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'import_odbc_demo.xml',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
}
