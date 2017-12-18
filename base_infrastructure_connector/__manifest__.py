# Copyright 2016-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Base Partner Validate Address',
    'summary': 'Provides an abstract interface/adapter mechanism allowing '
               'for the unification of address verification providers.',
    'version': '10.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'base_external_system',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/wizard_address_validate_view.xml',
    ],
}
