.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. image:: https://img.shields.io/badge/python-3.6-blue.svg
    :alt: Python support: 3.6
.. image:: https://app.travis-ci.com/OCA/odoo-module-migrator.svg?branch=master
    :target: https://app.travis-ci.com/OCA/odoo-module-migrator

====================
Views-migration-v17
====================

``views-migration-v17`` is a odoo server mode module that allows you to automatically migrate the views of a Odoo module versión <= v16 to v17 .

For example::

    <field name="test_field_1" attrs="{'invisible': [('active', '=', True)]}"/>
    <field name="test_field_2" attrs="{'invisible': [('zip', '!=', 123)]}"/>
    <field name="test_field_3" attrs="{'readonly': [('zip', '!=', False)]}"/>

To::

    <field name="test_field_1" invisible="active"/>
    <field name="test_field_2" invisible="zip != 123"/>
    <field name="test_field_3" readonly="zip"/>


Usage
=====

This module is not installable, to use this module, you need to:

1. Run odoo with this module as a server module:

.. code-block:: shell

  odoo -d DATABASE_NAME -i MODULE_TO_MIGRATE --load=base,web,views_migration_17 --stop-after-init


2. If success the modifications will be in the source code of your module.


Credits
=======

Authors
-------
* ADHOC SA


Contributors
------------
* `ADHOC SA <https://www.adhoc.com.ar>`_:

  * Juan José Scarafía <jjs@adhoc.com.ar>
  * Bruno Zanotti <bz@adhoc.com.ar>
