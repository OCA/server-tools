# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Point of Sale - Remove Enterprise Features',
    'version': '9.0.1.0.0',
    'category': 'Maintenance',
    'website': "https://laslabs.com",
    'author': 'LasLabs, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'views/res_config_view.xml',
    ]
}
