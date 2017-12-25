# -*- coding: utf-8 -*-
# Copyright <2011> <Daniel Reis>
# Copyright <2016> <Liu Jianyun>
# Copyright <2017> <Jesus Ramiro>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Import data from external data sources.',
    'version': '1.5',
    'category': 'Tools',
    'description': """
Import data directly from other databases.

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

Contributors
============

* Jesus Ramiro <jesus@bilbonet.net>
* Liu Jianyun <lnkdel@gmail.com>
* Maxime Chambreuil <maxime.chambreuil@savoirfairelinux.com>
* Daniel Reis, Odoo Community Association (OCA)
    """,
    'author': "Jesus Ramiro, Liu Jianyun, Daniel Reis, "
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/Bilbonet/server-tools',
    'images': [
        'images/snapshot1.png',
        'images/snapshot2.png',
    ],
    'depends': [
        'base',
        'base_external_dbsource',
    ],
    'data': [
        'views/base_external_import_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/base_external_import_demo.xml',
    ],
    'test': [],
    'installable': True,
    'active': False,
}
