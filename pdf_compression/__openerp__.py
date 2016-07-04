# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "PDF Compression",
    'summary': """compresses the pdf files for ir.attachement""",
    'author': "bloopark systems GmbH & Co. KG",
    'website': "http://www.bloopark.de",
    'category': 'attachement',
    'version': '1.0',
    'depends': [
        'report',
        'knowledge',
    ],
    'data': [
        'views/backend.xml',
        'data/ir_values.xml',
    ],
    'installable': True,
    'auto_install': False,
}
