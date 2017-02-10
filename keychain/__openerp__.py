# -*- coding: utf-8 -*-
# Copyright <2016> Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Keychain",
    "summary": "Store accounts and credentials",
    "version": "9.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://akretion.com/",
    "author": "Akretion, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [
            'cryptography'],
    },
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        'views/keychain_view.xml'
    ],
}
