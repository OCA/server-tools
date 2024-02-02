# -*- coding: utf-8 -*-
##############################################################################
#
#    Daniel Reis
#    2011
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
    'name': 'Import data from SQL and ODBC data sources.',
    'version': '1.3',
    'category': 'Tools',
    'description': """
Import data directly from other databases.

Installed in the Administration module, menu Configuration -> Import from SQL.

Features:
 * Fetched data from the databases are used to build lines equivalent to
   regular import files. These are imported using the standard "import_data()"
   ORM method, benefiting from all its features, including xml_ids.
 * Each table import is defined by an SQL statement, used to build the
   equivalent for an import file. Each column's name should match the column
   names you would use in an import file. The first column must provide an
   unique identifier for the record, and will be used to build its xml_id.
 * SQL columns named "none" are ignored. This can be used for the first column
   of the SQL, so that it's used to build the XML Id but it's not imported to
   any OpenERP field.
 * The last sync date is the last successfull execution can be used in the SQL
   using "%(sync)s", or ":sync" in the case of Oracle.
 * When errors are found, only the record with the error fails import. The
   other correct records are commited. However, the "last sync date" will only
   be automaticaly updated when no errors are found.
 * The import execution can be scheduled to run automatically.

Examples:
 * Importing suppliers to res.partner:
      SELECT distinct
            [SUPPLIER_CODE] as "ref"
          , [SUPPLIER_NAME] as "name"
          , 1 as "is_supplier"
          , [INFO] as "comment"
        FROM T_SUPPLIERS
       WHERE INACTIVE_DATE IS NULL and DATE_CHANGED >= %(sync)s

 * Importing products to product.product:
      SELECT PRODUCT_CODE as "ref"
           , PRODUCT_NAME as "name"
           , 'res_partner_id_'+SUPPLIER_ID as "partner_id/id"
        FROM T_PRODUCTS
       WHERE DATE_CHANGED >= %(sync)s

Improvements ideas waiting for a contributor:
 * Allow to import many2one fields (currently not supported). Done by adding a
   second SQL sentence to get child record list?
 * Allow "import sets" that can be executed at different time intervals using
   different scheduler jobs.
 * Allow to inactivate/delete OpenERP records when not present in an SQL
   result set.

Contributors
============

* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
    """,
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'license': 'AGPL-3',
    'images': [
        'images/snapshot1.png',
        'images/snapshot2.png',
    ],
    'depends': [
        'base',
        'base_external_dbsource',
    ],
    'data': [
        'import_odbc_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'import_odbc_demo.xml',
    ],
    'test': [],
    'installable': False,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
