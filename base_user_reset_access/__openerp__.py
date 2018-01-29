# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of base_user_reset_access,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     base_user_reset_access is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     base_user_reset_access is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with base_user_reset_access.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Base User Reset Access",
    'summary': """Reset User Access Right""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Tools',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'views/res_users_view.xml',
    ],
    'installable': False,
}
