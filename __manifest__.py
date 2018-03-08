# coding: utf-8
# Copyright (C) 2014 Therp BV (<http://therp.nl>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Fetch mail into inbox (invoice specific)",
    "version": "10.0.1.0.0",
    "author": "Therp BV",
    "category": "Accounting & Finance",
    "depends": [
        'account',
        'fetchmail_inbox',
    ],
    "data": [
        'view/mail_message.xml',
        'view/menu.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
    "license": "AGPL-3",
}
