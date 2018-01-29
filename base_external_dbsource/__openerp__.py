# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis, 2011
#    Additional contributions by Maxime Chambreuil, Savoir-faire Linux
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
    'name': 'External Database Sources',
    'version': '8.0.1.3.0',
    'category': 'Tools',
    'description': """
This module allows you to define connections to foreign databases using ODBC,
Oracle Client or SQLAlchemy.

Database sources can be configured in Settings > Configuration -> Data sources.

Depending on the database, you need:
 * to install unixodbc and python-pyodbc packages to use ODBC connections.
 * to install FreeTDS driver (tdsodbc package) and configure it through ODBC to
   connect to Microsoft SQL Server.
 * to install and configure Oracle Instant Client and cx_Oracle python library
   to connect to Oracle.

Contributors
============

* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
    """,
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'http://launchpad.net/addons-tko',
    'license': 'AGPL-3',
    'images': [
        'images/screenshot01.png',
    ],
    'depends': [
        'base',
    ],
    'data': [
        'base_external_dbsource_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'base_external_dbsource_demo.xml',
    ],
    'test': [
        'test/dbsource_connect.yml',
    ],
    'installable': False,
}
