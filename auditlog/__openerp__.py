# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 ABF OSIELL (<http://osiell.com>).
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
    'name': "Audit Log",
    'version': "8.0.1.0.0",
    'author': "ABF OSIELL,Odoo Community Association (OCA)",
    'website': "http://www.osiell.com",
    'category': "Tools",
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/auditlog_view.xml',
    ],
    'application': True,
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
