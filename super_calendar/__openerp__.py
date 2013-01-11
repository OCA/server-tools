# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
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

Configuration
=============

After installing the module you can go to

Super calendar → Configuration → Configurators

and create a new configurator. For instance, if you want to see meetings and phone calls, you can create the following lines

.. image:: http://planet.domsense.com/wp-content/uploads/2012/04/meetings.png
   :width: 400 px

.. image:: http://planet.domsense.com/wp-content/uploads/2012/04/phone_calls.png
   :width: 400 px

Then, you can use the ‘Generate Calendar’ button or wait for the scheduled action (‘Generate Calendar Records’) to be run.

When the calendar is generated, you can visualize it by the ‘super calendar’ main menu.

Here is a sample monthly calendar:

.. image:: http://planet.domsense.com/wp-content/uploads/2012/04/month_calendar.png
   :width: 400 px

And here is the weekly one:

.. image:: http://planet.domsense.com/wp-content/uploads/2012/04/week_calendar.png
   :width: 400 px

As you can see, several filters are available. A typical usage consists in filtering by ‘Configurator’ (if you have several configurators, ‘Scheduled calls and meetings’ can be one of them) and by your user. Once you filtered, you can save the filter as ‘Advanced filter’ or even add it to a dashboard.
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
