.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

=======================
Red October Attachments
=======================

This module provides a ``red_october`` type to ``ir.attachment``, which provides
encryption and decryption services using a remote Red October instance.


Installation
============

A working Red October installation is required to use this module.

* Install the Python Red October library ``pip install git+https://github.com/LasLabs/python-red-october@feature/master/code-samples``

Configuration
=============

* Go to ``Settings => Crypto => Vaults`` to create and manage vaults.
  * Vault must be initialized in ``Action => Init Vault`` from vault form view.
* Manage crypto users in ``Settings => Crypto => Vaults``.

Usage
=====

* Create an Attachment of Type ``Red October``.
* Manage delegations in ``Settings => Crypto => Delegations``.

Note that there must be a valid rights delegation on the Vault in order to decrypt a file,
even if you are the only owner.

Developers looking to implement this functionality should use an ``ir.attachment``
field set to type ``red_october``.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0 for server-tools

Known issues / Roadmap
======================

* Decouple the Red October user passwords from Odoo passwords.
* Allow for multiple RedOctoberUsers per ResUser, with a selection controlled via the session.
* Allow for multiple RedOctoberVaults per ResCompany.
* Allow transferring files between vaults.
* If decrypt error, fail silently & instead hide the data. Need to handle in the encrypt too.
* Add delegation uses & delta to ``red.october.file.owner``.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Dave Lasley <dave@laslabs.com>

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
