# Copyright 2022 Yannick Buron <yannick.buron@gmail.com>
{
    'name': "External Datasource - Exemple",
    'summary':
    'Exemple use of external datasource, using the current base as datasource',
    "development_status": "Alpha",
    'version': '12.0.1.0.0',
    'author': (
        'Yannick Buron',
        'Odoo Community Association (OCA)'
    ),
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
    'category': 'Hidden/Dependency',
    'depends': [
        'base',
        'mail',
        'sale',
        'web_external_odoo'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/orders.xml',
        'views/templates.xml',
    ],
    'installable': True,
}
