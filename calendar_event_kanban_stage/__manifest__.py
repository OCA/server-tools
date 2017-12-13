# -*- coding: utf-8 -*-
# Copyright 2017 Alex Comba - Agile Business Group
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    'name': 'Calendar Event Kanban Stage',
    'summary': 'Adds Kanban stage functionality to calendar event',
    'version': '10.0.1.0.0',
    'author': 'Agile Business Group, '
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'website': 'https://www.agilebg.com',
    'category': 'Tools',
    'depends': [
        'calendar',
        'base_kanban_stage',
    ],
    'data': [
        'data/base_kanban_stage_data.xml',
        'views/calendar_event_view.xml',
    ],
    'installable': True,
}
