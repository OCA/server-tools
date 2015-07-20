# -*- coding: utf-8 -*-
##############################################################################
#
#    Module for Odoo
#
#    Copyright (c) All rights reserved:
#        (c) 2013      ABF OSIELL (<http://osiell.com>).
#                      Holger Brunn <hbrunn@therp.nl>
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
    'name': 'Audit Log',
    'version': '1.1',
    'author': 'Odoo Community Association (OCA), '
              'ABF OSIELL',
    'contributors': [
        'Holger Brunn <hbrunn@therp.nl>, '
        'Juan Formoso <jfv@anubia.es>, '
        'Alejandro Santana <alejandrosantana@anubia.es>',
    ],
    'summary': 'Log CRUD operations',
    'website': 'http://www.osiell.com',
    'category': 'Tools',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/auditlog_view.xml',
        'wizards/auditlog_all_models_view.xml',
    ],
    'application': True,
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
