# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2010 - 2014 Savoir-faire Linux
#    (<http://www.savoirfairelinux.com>).
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
    'name': 'Prototype',
    'version': '0.1',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'AGPL-3',
    'category': 'Others',
    'summary': 'Prototype your module',
    'description': """
This module allows the administrator to prototype new features and export
them as module.

Usage
=====

Go to Settings > Modules > Prototype, create a new prototype, fill in the
information and export your module.

Contributors
============

* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Savoir-faire Linux <support@savoirfairelinux.com>

More information
----------------
* Module developed and tested with Odoo version 8.0
* For questions, please contact our support services
(support@savoirfairelinux.com)
""",
    'depends': [
        'base',
    ],
    'external_dependencies': {
        'python': [],
    },
    'data': [
        'wizard/prototype_module_export_view.xml',
        'views/prototype_view.xml',
        'views/ir_model_fields_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
