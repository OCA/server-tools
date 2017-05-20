Track user operation on data models (asynchronous mode)
=======================================================

This module overrides the ``auditlog`` module to make asynchronous the
log creation, resulting in greater performance and a better user experience.

Usage
=====

This module uses the ``connector`` framework to delay the log creation in a
job queue.

To take advantage of this module, you have to:

 * run `Odoo` in multiprocess mode (``workers`` > 0)
 * start `Odoo` with the ``ODOO_CONNECTOR_CHANNELS`` environment variable
   defined and ``--load=web,connector``

For further information, please visit:

 * http://odoo-connector.com/guides/jobrunner.html#how-to-use-it
 * https://www.odoo.com/forum/help-1

Credits
=======

Contributors
------------

* Sebastien Alix <sebastien.alix@osiell.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
