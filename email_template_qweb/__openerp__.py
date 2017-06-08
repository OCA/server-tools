# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "QWeb for email templates",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Marketing",
    "summary": "Use the QWeb templating mechanism for emails",
    "depends": [
        'email_template',
    ],
    "demo": [
        "demo/ir_ui_view.xml",
        "demo/email_template.xml",
    ],
    "data": [
        "views/email_template.xml",
    ],
}
