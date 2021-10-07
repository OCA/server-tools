# -*- coding: utf-8 -*-
# Copyright 2017 Lorenzo Battistini - Agile Business Group
# Copyright 2017 Alex Comba - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).
{
    "name": "Read only user",
    "version": "12.0.1.0.0",
    'category': 'Tools',
    'summary': "Allows to configure a user as 'readonly'",
    "website": "https://github.com/OCA/server-tools",
    "author": "Agile Business Group, Odoo Community Association (OCA)",
    "license": "GPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "base",
    ],
    "data": [
        "views/user_view.xml",
    ],
}
