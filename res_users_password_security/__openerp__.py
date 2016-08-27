# -*- coding: utf-8 -*-
# Copyright 2015 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{

    'name': 'Password Security',
    "summary": "Allow admin to set password security requirements.",
    'version': '9.0.1.0.1',
    'author': "LasLabs, Odoo Community Association (OCA)",
    'category': 'Base',
    'depends': [
        'auth_crypt',
        'auth_signup',
    ],
    "website": "https://laslabs.com",
    "licence": "LGPL-3",
    "data": [
        'views/res_company_view.xml',
    ],
    'installable': True,
}
