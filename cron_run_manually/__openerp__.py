# -*- coding: utf-8 -*-

# OpenERP, Open Source Management Solution
# This module copyright (C) 2013 Therp BV (<http://therp.nl>)
# Code snippets from openobject-server copyright (C) 2004-2013 OpenERP S.A.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

{
    'name': 'Call cron jobs from their form view',
    'version': '8.0.1.0.0',
    'author': "Therp BV (OpenERP S.A.),Odoo Community Association (OCA)",
    'license': 'AGPL-3',
    'category': 'Tools',
    'description': """
This module adds a button to the cron scheduled task form in OpenERP
that allows the administrator to run the job immediately, independently
of the scheduler.
""",
    'depends': ['base', 'mail'],
    'data': ['view/ir_cron.xml'],
    "test": [
        "tests/correct_uid.yml",
    ],
    'installable': True,
    'auto_install': True,
}
