CLI shell for Odoo
==================

Makes available in Odoo 8 the `shell` server command available for Odoo 9.

Installation
============

Just install the module.

Configuration
=============

Nothing special to be configured.

Usage
=====

To have this feature available this module just need to be in the
addons path. To use it, in a terminal window run:

    $ ./odoo.py shell -d <dbname>

This will initialize a server instance and then jump into a Pyhton
interactive shell, with full access to the Odoo API.

Example session:

    >>> self
    res.users(1,)
    >>> self.name
    u'Administrator'
    >>> self._name
    'res.users'
    >>> self.env
    <openerp.api.Environment object at 0xb3f4f52c>
    >>> self.env['res.partner'].search([('name', 'like', 'Ag')])
    res.partner(7, 51)



Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20shell%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* OpenERP S.A.
* Daniel Reis <dgreis@sapo.pt>

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
