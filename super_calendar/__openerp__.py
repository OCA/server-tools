# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Super Calendar",
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'description': """
    This module allows to create configurable calendars.
    
    Through the 'calendar configurator' object, you can specify which models have to be merged in the super calendar. For each model, you have to define the 'description' and 'date_start' fields at least. Then you can define 'duration' and the 'user_id' fields.
    
    The 'super.calendar' object contains the the merged calendars. The 'super.calendar' can be updated by 'ir.cron' or manually.
    """,
    'author': 'Agile Business Group & Domsense',
    'website': 'http://www.agilebg.com',
    'license': 'AGPL-3',
    "depends" : ['base'],
    "init_xml" : [],
    "update_xml" : [
        'super_calendar_view.xml',
        'cron_data.xml',
        'security/ir.model.access.csv',
        ],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
