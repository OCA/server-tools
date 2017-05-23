.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Audit Log Easy Config
=====================

This module was written to extend the functionality of the *Audit Log* module
(technical name *auditlog*) to make it more comfortable and quick in its
configuration. Options added in this extension are:

* Rules multi-creation: create and subscribe a rule for each existing model
  in the database, setting the type of actions you want to track (creations,
  updates or deletions).
* Rules multi-subscription: subscribe selected rules in the tree view.
* Rules multi-unsubscription: unsubscribe selected rules in the tree view.
* Rules multi-edit: modify trcked actions in selected rules in the tree view.

Installation
============

To install this module, you need to:

* Check that you have the *Audit Log* (technical name *auditlog*) module
  available in your modules list, and if so, install *Audit Log Easy Config*
  (technical name *auditlog_easy_config*) module.

Usage
=====

To use this module, you need to:

* You will be able to see the implemented options only if
  you have *Settings* as the *Administration* access rights.
  If so, go to *Reporting*, section *Audit*.

Known issues / Roadmap
======================

* Translate the module to other languages.

Credits
=======

Contributors
------------

* Juan Formoso <jfv@anubia.es>
* Alejandro Santana <alejandrosantana@anubia.es>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
