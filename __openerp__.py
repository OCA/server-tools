# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Fetch mail into inbox",
    "version": "8.0.1.0.0",
    "author": "Therp BV",
    "category": "Dependency",
    "depends": [
        'mail',
        'fetchmail',
    ],
    "data": [
        "security/res_groups.xml",
        "wizard/fetchmail_inbox_create_wizard.xml",
        "wizard/fetchmail_inbox_attach_existing_wizard.xml",
        "view/mail_message.xml",
        "view/menu.xml",
        'security/ir.model.access.csv',
    ],
}
