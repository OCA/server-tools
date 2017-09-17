.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===========================================
Import data from SQL and ODBC data sources.
===========================================

This module allows import data directly from other databases.

Usage
=====

Go to: Administration module, menu Configuration -> Import from SQL.

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
 * The last sync date is the last successfull execution can be used in the SQL:
   Using "CAST(? as datetime)" in the case of MSSQL.
   Using "%(sync)s", or ":sync" in the case of Oracle.
 * When errors are found, only the record with the error fails import. The
   other correct records are commited. However, the "last sync date" will only
   be automaticaly updated when no errors are found.
 * The import execution can be scheduled to run automatically.

Examples:
 * Importing suppliers to res.partner:
    ::

        SELECT distinct[SUPPLIER_CODE] as "ref",
            [SUPPLIER_NAME] as "name",
            'True' as "is_supplier",
            [INFO] as "comment"
        FROM T_SUPPLIERS
        WHERE INACTIVE_DATE IS NULL and DATE_CHANGED >= CAST(? as datetime)

 * Importing products to product.product:
    ::

        SELECT
            PRODUCT_CODE as "ref",
            PRODUCT_NAME as "name",
            'res_partner_id_' + SUPPLIER_ID as "partner_id/id"
        FROM T_PRODUCTS
        WHERE DATE_CHANGED >= CAST(? as datetime)


Known issues / Roadmap
======================
Improvements ideas waiting for a contributor:
 * Allow to import many2one fields (currently not supported). Done by adding a
   second SQL sentence to get child record list?
 * Allow "import sets" that can be executed at different time intervals using
   different scheduler jobs.
 * Allow to inactivate/delete Odoo records when not present in an SQL
   result set.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20import_odbc%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Daniel Reis <dreis.pt@gmail.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Jesus Ramiro <jesus@bilbonet.net>


Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.