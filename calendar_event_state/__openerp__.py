# -*- coding: utf-8 -*-
# © 2016 Alessio Gerace - Agile Business Group
# © 2016 Lorenzo Battistini - Agile Business Group
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

{
    "name": "Calendar Event state",
    "summary": "Custom states, on calendar events",
    "version": "8.0.1.0.0",
    "author": "Agile Business Group, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
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
