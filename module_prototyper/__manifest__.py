# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'Module Prototyper',
    'version': '10.0.1.0.0',
    'author': 'Savoir-faire Linux, Sudokeys, Onestein, '
              'Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'https://github.com/OCA/server-tools'
               '/tree/10.0/module_prototyper',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Prototype your module.',
    'depends': [],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'data/module_prototyper_api_version_data.xml',
        'wizard/module_prototyper_module_export_view.xml',
        'views/module_prototyper_view.xml',
        'views/ir_model_fields_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
