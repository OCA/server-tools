# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{

    'name': 'Website Password Security',
    "summary": "Glue module for when website is installed.",
    'version': '10.0.1.0.0',
    'author': "LasLabs, Odoo Community Association (OCA)",
    'category': 'Base',
    'depends': [
        'password_security',
        'website',
    ],
    "website": "https://laslabs.com",
    "license": "LGPL-3",
    "data": [
        'templates/website_template.xml',
    ],
    'installable': True,
    'auto_install': True,
}
