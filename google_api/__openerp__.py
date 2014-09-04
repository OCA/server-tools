# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Solutions2use (<http://www.solutions2use.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name' : 'google_api',
    'author' : 'solutions2use',
    'website' : "http://www.solutions2use.com",
    'version' : "1.0",
    "depends" : ['base_calendar'],
    'description': """
	OpenERP solution for synchronizing crm_meeting with google calendar
	visit http://www.solutions2use.com/google-calendar for installation details
	""",
    'category' : 'Google Apps',
    'data': [
             'data/scheduler.xml',
             'security/res_groups.xml',
             'security/ir.model.access.csv',
             'view/google_calendar_view.xml'
             ],
    'demo': [],
    'test': [],
    'active': False,
    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

