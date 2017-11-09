# -*- encoding: utf-8 -*-
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
    'version': '8.0.0.3.0',
    'author': 'Savoir-faire Linux, Odoo Community Association (OCA)',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Prototype your module.',
    'depends': [
        'admin_technical_features',
    ],
    'external_dependencies': {
        'python': ['xoutil>=1.7.0,<1.8',],
    },
    'data': [
        'wizard/module_prototyper_module_export_view.xml',
        'views/module_prototyper_view.xml',
        'views/ir_model_fields_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
}
