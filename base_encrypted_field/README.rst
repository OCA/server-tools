.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

================
Encrypted fields
================

This module was written to allow users to encrypt arbitrary fields on a record.
Fields are encrypted on a per record base on the client side, passphrases will
never be uploaded to the server.

Technically, this works by assigning a PGP key pair to every user. This key is
used to encrypt a symmetric key generated for every encryption group for every
member of this group.

Installation
============

To install this module, you need to:

* do this ...

Configuration
=============

To configure this module, you need to:

* go to ...

Usage
=====

To use this module, you need to:

* go to ...
.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/{repo_id}/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt

For further information, please visit:

* https://www.odoo.com/forum/help-1

Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20base_encrypted_field%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Libraries
---------

* https://github.com/openpgpjs/openpgpjs
* https://keybase.io/triplesec

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
