# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Infrastructure',
    'summary': 'Provides models and methods required for connecting Odoo '
               'with infrastructure orchestration systems.',
    'version': '10.0.1.0.0',
    'category': 'Extra Tools',
    'website': 'https://laslabs.com/',
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'application': True,
    'installable': True,
    'depends': [
        'base_external_system',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/wizard_address_validate_view.xml',
    ],
}
