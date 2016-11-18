# -*- coding: utf-8 -*-
# Copyright 2016 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{

    'name': 'API Foreach',
    "summary": "It provides an API decorator that auto iterates recordsets.",
    'version': '10.0.1.0.0',
    'author': "LasLabs, Odoo Community Association (OCA)",
    'category': 'Base',
    'depends': [
        'base',
    ],
    "website": "https://laslabs.com",
    "license": "LGPL-3",
    'post_load': '_patch_api',
    'installable': True,
}
