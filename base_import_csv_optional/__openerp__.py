# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#
#    Copyright (c) All rights reserved:
#        (c) 2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Alejandro Santana <alejandrosantana@anubia.es>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#
##############################################################################
{
    'name': 'Optional CSV import',
    'version': '1.0',
    'category': 'Server tools',
    'summary': 'Group-based permissions for importing CSV files',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), '
              'Alejandro Santana <alejandrosantana@anubia.es>',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'http://odoo-community.org',
    'depends': [
        'base_import'
    ],
    'data': [
        'security/base_import_csv_optional_security.xml',
        'views/base_import.xml',
    ],
    'js': [
        'static/src/js/import.js',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
