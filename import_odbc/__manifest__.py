# -*- coding: utf-8 -*-
# Copyright <2011> <Daniel Reis>
# Copyright <2017> <Jesus Ramiro>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Import data from SQL and ODBC data sources.',
    'version': '10.0.1.0.0',
    'category': 'Tools',
    'author': "Daniel Reis, "
              "Jesus Ramiro, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/server-tools',
    'license': 'LGPL-3',
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
   any Odoo field.
 * The last sync date is the last successfull execution can be used in the SQL
   using "CAST(? as datetime)" in the case of MSSQL.
   Using "%(sync)s", or ":sync" in the case of Oracle.
 * When errors are found, only the record with the error fails import. The
   other correct records are commited. However, the "last sync date" will only
   be automaticaly updated when no errors are found.
 * The import execution can be scheduled to run automatically.

Examples:
 * Importing suppliers to res.partner:
      SELECT distinct
            [SUPPLIER_CODE] as "ref"
          , [SUPPLIER_NAME] as "name"
          , 'True' as "is_supplier"
          , [INFO] as "comment"
        FROM T_SUPPLIERS
       WHERE INACTIVE_DATE IS NULL and DATE_CHANGED >= CAST(? as datetime)

 * Importing products to product.product:
      SELECT PRODUCT_CODE as "ref"
           , PRODUCT_NAME as "name"
           , 'res_partner_id_'+SUPPLIER_ID as "partner_id/id"
        FROM T_PRODUCTS
       WHERE DATE_CHANGED >= CAST(? as datetime)

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
    'images': [
        'images/snapshot1.png',
        'images/snapshot2.png',
    ],
    'depends': [
        'base',
        'base_external_dbsource',
    ],
    'data': [
        'views/import_odbc_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/import_odbc_demo.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
}

