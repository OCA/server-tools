# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014-2015 Daniel Reis
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
    'name': 'Automated Agent Bots',
    'version': '8.0.1.0.0',
    'category': 'Tools',
    'author': 'Daniel Reis, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/server-tools',
    'depends': [
        'base_action_rule',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/action_fact_view.xml',
        'views/action_ruleset_view.xml',
        'views/action_rule_view.xml',
    ],
    'demo': [],
    'application': True,
    'installable': True,
}
