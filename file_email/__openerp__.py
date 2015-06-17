# -*- coding: utf-8 -*-
###############################################################################
#
#   file_email for OpenERP
#   Copyright (C) 2012-TODAY Akretion <http://www.akretion.com>.
#   @author Sébastien BEAU <sebastien.beau@akretion.com>
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
    'name': 'file_email',
    'version': '0.1',
    'category': 'Generic Modules/Others',
    'license': 'AGPL-3',
    'description': """Abstract module for importing and processing the
    attachment of an email. The attachment of the email will be imported
    as a attachment_metadata and then in your custom module you can process it.
    An example of processing can be found in account_statement_email
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com/',
    'depends': ['external_file_location', 'fetchmail'],
    'init_xml': [],
    'update_xml': [
        "fetchmail_view.xml",
        "attachment_metadata_view.xml",
        ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
