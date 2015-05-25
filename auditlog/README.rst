.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

Track user operation on data models
===================================

This module allows the administrators to:

* log user operations performed on data models such as
  ``create``, ``read``, ``write`` and ``delete``,
* create and subscribe a rule for each existing model
  in the database at once, setting the type of actions
  you want to track (creations, updates or deletions),
* subscribe selected rules in the tree view at once,
* unsubscribe selected rules in the tree view at once,
* modify tracked actions in selected rules in the tree
  view at once.

Usage
=====

* Go to `Reporting / Audit / Rules` to subscribe rules. A rule defines which
  operations to log for a given data model.
* Then, check logs in the `Reporting / Audit / Logs` menu.
* To create and subscribe a rule for each model currently in the database
  all at once, click on `Reporting / Audit / Set rules for every model`.
  In the popup wizard you can set which actions to track
  (create, write, unlink) and if you want to overwrite existing rules
  configuration.
* Also, within `Reporting / Audit / Rules` list view, you can select any
  number of rules. Then, within the "More" button above, you can select
  to subscribe, unsubscribe or edit tracked actions for those selected rules.

**NOTES:**

* These functionalities will only be available for users in
  `Administration / Access Rights` group or higher.
* During installation, it will migrate any existing data from the `audittrail`
  module (rules and logs).

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* log ``read`` operations
* log only operations triggered by some users (currently it logs all users)
* group logs by HTTP query (thanks to werkzeug)?
* group HTTP query by user session?

Credits
=======

Contributors
------------

* Sebastien Alix <sebastien.alix@osiell.com>
* Holger Brunn <hbrunn@therp.nl>
* Juan Formoso <jfv@anubia.es>
* Alejandro Santana <alejandrosantana@anubia.es>

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
