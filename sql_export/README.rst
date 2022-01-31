.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

SQL Export
==========

Allow to export data in csv files FROM sql requests.
There are some restrictions in the sql sql request, you can only read datas.
No update, deletion or creation are possible.
A new menu named Export is created.

Known issues / Roadmap
======================

* Some words are prohibeted and can't be used is the query in anyways, even in a select query :
    * delete
    * drop
    * insert
    * alter
    * truncate
    * execute
    * create
    * update

See sql_request_abstract module to fix this issue.

* checking SQL request by execution and rollback is disabled in this module
  since variables features has been introduced. This can be fixed by
  overloading _prepare_request_check_execution() function.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Florian da Costa <florian.dacosta@akretion.com>

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
