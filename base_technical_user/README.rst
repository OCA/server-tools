.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================
Base Technical User
===================

This module extends the functionality of company management.
It allows you to bind a technical user on the company in order to use it in
batch processes.

The technical user must
- be inactive to avoid login
- be in the required groups depending of what you need to do

Usage
=====

If you install the module, you will find a tab on the company form allowing
to define the technical user.


In your code you can use the following helper that will return you

- a self with the user tech if configured
- or a self with sudo user

.. code-block:: python

    self_tech = self.sudo_tech()

If you want to raise an error if the tech user in not configured just call it with

.. code-block:: python

    self_tech = self.sudo_tech(raise_if_missing)


Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Cédric Pigeon <cedric.pigeon@acsone.eu>
* Sébastien BEAU <sebastien.beau@akretion.com>

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
