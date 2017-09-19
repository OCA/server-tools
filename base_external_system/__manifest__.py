# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Base External System",
    "summary": "Data models allowing for connection to external systems.",
    "version": "10.0.1.0.0",
    "category": "Base",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    'depends': [
        'base',
    ],
    'data': [
        'views/external_system_view.xml',
    ],
}
