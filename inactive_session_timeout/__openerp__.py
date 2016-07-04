# -*- coding: utf-8 -*-
##############################################################################

#     This file is part of inactive_session_timeout, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     inactive_session_timeout is free software: you can redistribute it
#     and/or modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     inactive_session_timeout is distributed in the hope that it will
#     be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with inactive_session_timeout.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Inactive Sessions Timeout",

    'summary': """
        This module disable all inactive sessions since a given delay""",

    'author': "ACSONE SA/NV", "Odoo Community Association (OCA)"
    'website': "http://acsone.eu",

    'category': 'Tools',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',

    'depends': [
        'base',
    ],

    'data': [
        'data/ir_config_parameter_data.xml'
    ]
}
