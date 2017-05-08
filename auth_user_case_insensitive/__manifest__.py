# -*- coding: utf-8 -*-
# Copyright 2015-2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
{
    "name": "Case Insensitive Logins",
    "summary": "Makes the user login field case insensitive",
    "version": "10.0.1.0.0",
    "category": "Authentication",
    "website": "https://laslabs.com/",
    "author": "LasLabs, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    'installable': True,
    "depends": [
        "mail",
    ],
    'pre_init_hook': 'pre_init_hook_login_check',
    'post_init_hook': 'post_init_hook_login_convert',
}
