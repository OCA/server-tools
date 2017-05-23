# -*- coding: utf-8 -*-
##############################################################################
#
#    Module for Odoo
#
#    Copyright (c) All rights reserved:
#        (c) 2015      Anubía, soluciones en la nube,SL (http://www.anubia.es)
#                      Juan Formoso <jfv@anubia.es>,
#                      Alejandro Santana <alejandrosantana@anubia.es>
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
    'name': 'Audit Log Easy Config',
    'summary': 'Auditlog config all models in the database',
    'version': '0.2',
    'category': 'Tools',
    'license': 'AGPL-3',
    'author': 'Odoo Community Association (OCA), '
              'Juan Formoso <jfv@anubia.es>, '
              'Alejandro Santana <alejandrosantana@anubia.es>',
    'maintainer': 'Odoo Community Association (OCA)',
    'website': 'http://odoo-community.org',
    'depends': [
        'auditlog',
    ],
    'data': [
         'security/ir.model.access.csv',
         'wizards/auditlog_all_models_view.xml',
         'views/auditlog_rule_view.xml',
    ],
    'installable': True,
}
