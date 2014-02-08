# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
    'name': 'Database cleanup',
    'version': '0.1',
    'author': 'Therp BV',
    'depends': ['base'],
    'license': 'AGPL-3',
    'category': 'Tools',
    'data': [
        'view/purge_modules.xml',
        'view/purge_models.xml',
        'view/purge_columns.xml',
        'view/purge_tables.xml',
        'view/purge_data.xml',
        'view/menu.xml',
        ],
    'description': """\
Clean your OpenERP database from remnants of modules, models, columns and
tables left by uninstalled modules (prior to 7.0) or a homebrew database
upgrade to a new major version of OpenERP.

After installation of this module, go to the Settings menu -> Technical ->
Database cleanup. Go through the modules, models, columns and tables
entries under this menu (in that order) and find out if there is orphaned data
in your database. You can either delete entries by line, or sweep all entries
in one big step (if you are *really* confident).

Caution! This module is potentially harmful and can *easily* destroy the
integrity of your data. Do not use if you are not entirely comfortable
with the technical details of the OpenERP data model of *all* the modules
that have ever been installed on your database, and do not purge any module,
model, column or table if you do not know exactly what you are doing.
""",

}
