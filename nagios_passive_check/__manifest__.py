# Copyright 2018 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Nagios passive check',
    'summary': 'Report Odoo state to nagios',
    'version': '11.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://github.com/OCA/server-tools',
    'author': 'Creu Blanca,'
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base', 'bus',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'views/nagios_server_views.xml',
    ]
}
