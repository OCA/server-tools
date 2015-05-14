# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Odoo Source Management Solution
#    Copyright (c) 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
    'name': 'Translations bot',
    'version': '1.0',
    'category': 'Website',
    'author': 'Serv. Tecnolog. Avanzados - Pedro M. Baeza',
    'website': 'http://www.serviciosbaeza.com',
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python': ['github', 'txlib'],
    },
    'data': [
        'data/ir_cron.xml',
        'views/transbot_menus.xml',
        'views/transbot_project_view.xml',
        'views/transbot_log_view.xml',
        'views/res_config_view.xml',
        'security/ir.model.access.csv',
    ],
    "installable": True,
}
