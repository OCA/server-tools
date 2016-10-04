.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Materialized SQL View
=====================


This odoo module, add utilities to manage materialized SQL view
and necessary user interface to interact with.

How to use it
-------------

You can have a look to `the basic example
<https://github.com/OCA/server-tools/blob/8.0/test_materialized_sql_view/model/
model_test_using_sql_mat_view.py>`_,
used in test module: `test_materialized_sql_view`.

You can etheir add cron to refresh the materialized view periodically,
`here <https://github.com/OCA/server-tools/blob/8.0/test_materialized_sql_view/
data/ir_cron.xml>`
an example on the previous model


Features
--------

* UI to manage materialized Sql view, and manually launch refresh
    - add `Materialized sql view Manager` group to your expected user.
    - Go through `Settings > Technical > Database Structure >
      Materialized SQL view` menu to manage materialized sql views
* Abstract class, to help developer to create materialized sql view
* Use Postgresql materialized view if pg >= 9.3.0.
* Manage when pg version changed
* Recreate materialized sql view only if necessary, one of those change:
  - sql materialized view name `_sql_mat_view_name`, this is used as search key
    (so if you change it, you have to manage how to clean unecessary views and
    records)
  - sql definition has changed `_sql_view_definition`
  - sql view name has changed `_sql_view_name`
  - database version has changed


Roadmap
-------

* Add UI on models based on materialized view Specially on dashboards to tell
  last refresh date


Credits
=======
Images
------

* Odoo Community Association:

.. image:: https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg
   :alt: Odoo Community Association
   :target: https://odoo-community.org

* Anybox

.. image:: https://anybox.fr/logo.png
   :alt: Anybox
   :target: https://anybox.fr/logo.png

Contributors
------------

* Pierre Verkest <pverkest@anybox.fr>

Maintainer
----------


.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
