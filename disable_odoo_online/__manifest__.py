# -*- coding: utf-8 -*-
# Copyright (C) 2013 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Remove odoo.com Bindings",
    "version": "11.0.1.0.0",
    "author": "Therp BV,GRAP,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "base",
    "depends": [
        'base',
        'mail',
    ],
    "data": [
        'views/ir_ui_menu.xml',
        'data/ir_cron.xml',
    ],
    "qweb": [
        'static/src/xml/base.xml',
    ],
    'installable': True,
}
