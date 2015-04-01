Track user operation on data models
===================================

This module allows the administrator to log user operations performed on data
models such as ``create``, ``read``, ``write`` and ``delete``.

Usage
=====

Go to `Reporting / Audit / Rules` to subscribe rules. A rule defines which
operations to log for a given data model.
Then, check logs in the `Reporting / Audit / Logs` menu.

During installation, it will migrate any existing data from the `audittrail`
module (rules and logs).

For further information, please visit:

 * https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

 * log only operations triggered by some users (currently it logs all users)
 * group logs by HTTP query (thanks to werzeug)?
 * group HTTP query by user session?

Credits
=======

Contributors
------------

* Sebastien Alix <sebastien.alix@osiell.com>
* Holger Brunn <hbrunn@therp.nl>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
