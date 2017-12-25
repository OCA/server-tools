.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===========================================
Import data from external data sources.
===========================================

This module allows import data directly from other databases.

Usage
=====

Installed in the Administration module, menu Settings -> Technical ->
Database Structure -> External Import Task.

Features:
 * Fetched data from the databases are used to build lines equivalent to
   regular import files. These are imported using the standard "load()"
   ORM method, same as regular import function, benefiting from all its
   features, including xml_ids.
 * Each table import is defined by an SQL statement, used to build the
   equivalent for an import file. Each column's name should match the column
   names you would use in an import file. No column can called "id" and
   The first column must provide an unique identifier for the record,
   and will be used to build its xml_id.
 * Allow to import many2one fields, same as regular import module.
 * The last sync date is the last successfully execution can be used in the SQL
   using "%(sync)s", or ":sync" in the case of Oracle.
 * When errors are found, only the record with the error fails import. The
   other correct records are committed. However, the "last sync date" will only
   be automatically updated when no errors are found.
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



Credits
=======

Contributors
------------

* Jesus Ramiro <jesus@bilbonet.net>
* Liu Jianyun <lnkdel@gmail.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Daniel Reis, Odoo Community Association (OCA)

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.