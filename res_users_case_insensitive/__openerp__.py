# -*- coding: utf-8 -*-
# © 2015-TODAY LasLabs Inc.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Case Insensitive Logins",
    "summary": "Makes the login field of res.users case insensitive.",
    "version": "9.0.1.0.0",
    "category": "Base",
    'depends': [
        'mail',  # Required if shares branch with password_security module
    ],
    "website": "https://laslabs.com/",
    "author": "LasLabs",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
}
