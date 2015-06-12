# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    This module copyright (C) $export_date $author
#    (<$website>).
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
    'name': '$name',
    'version': '$version',
    'author': '$author',
    'maintainer': '$maintainer',
    'website': '$website',
    'license': 'AGPL-3',
    'category': '$category',
    'summary': '$summary',
    'description': """
$description

* Module exported by the prototype module for version 8.0.
* If you have any questions, please contact Savoir-faire Linux \
(support@savoirfairelinux.com)
""",
    'depends': [
        $depends
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        $data
    ],
    'installable': True,
    'auto_install': $auto_install,
}
