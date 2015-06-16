# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Server Action Email Translate',
    'version': '1.0',
    'author': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'category': 'other',
    'license': 'AGPL-3',
    'description': """
Server Action Email Translate
=============================

This module allows to translate server action email messages in the
recipient's language.

The message will be translated in the admin user's language if
the recipient is not found in the system.
    """,
    'depends': [
        'base',
    ],
    'data': [
    ],
    'demo': [],
    'test': [],
    'external_dependencies': {
        'python': ['num2words'],
    },
    'installable': True,
}
