# -*- coding: utf-8 -*-
# Copyright 2016 Alessio Gerace - Agile Business Group
# Copyright 2016-2017 Lorenzo Battistini - Agile Business Group
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "Calendar Event state",
    "summary": "Custom states on calendar event",
    "version": "10.0.1.0.0",
    "author": "Agile Business Group, "
              "Odoo Community Association (OCA)",
    "license": "LGPL-3",
    "website": 'http://www.agilebg.com',
    "category": "Tools",
    "depends": ['calendar'],
    'installable': True,
    "data": [
        "data/calendar_state_data.xml",
        "security/ir.model.access.csv",
        "views/calendar_view.xml",
        "views/company_view.xml",
    ],

}
