# -​*- coding: utf-8 -*​-
##############################################################################
#
#    Copyright 2009-2016 Trobz (<http://trobz.com>).
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
    'name': 'Security Safe Password',
    'version': '9.0.1.0.0',
    'category': 'Authentication',
    'license': 'AGPL-3',
    'author': 'Trobz, Odoo Community Association (OCA)',
    'summary': 'Add constraints to strengthen user password',
    'installable': True,
    'auto_install': False,
    'application': False,
    'depends': [
        'base'
    ],
    'data': [
        'data/ir_config_parameter_data.xml',
    ],
    'external_dependencies': {
        'python': ['cracklib'],
    },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
