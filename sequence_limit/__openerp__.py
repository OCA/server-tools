# -*- encoding: utf-8 -*-
###############################################################################
#
#  sequence_limit for OpenERP
#  Copyright (C) 2012-14 Akretion Chafique DELLI <chafique.delli@akretion.com>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################


{
    'name': 'Sequence_Limit',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'licence': 'AGPL-3',
    'description': """
Module for warning pop-up upon reaching the maximum number or deadline of sequence.
Can be used for example by e-tailers, in the case of editing shipping label
when the transport company attribute a series of revolving number for each type of shipping label.
Well, the module can be alerted when approaching the last number component series.
    """,
    'author': 'AKRETION',
    'website': 'http://wwww.akretion.com/',
    'depends': ['base',
                'email_template',
                ],
    'data': [
        'ir_sequence_view.xml',
        'sequence_limit_mail_template.xml',
    ],
    'demo': [],
    'installable': 'true',
    'active': 'false',
}
