.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

==============
SFTP Connector
==============

This module allows you to connect & interact with remote SFTP hosts.

This module does not provide functionality on its own, it is meant to provide
an abstract SFTP core to be utilized by other business logic.

Installation
============

To install this module, you need to:

* Install paramiko
  ``pip install paramiko``

Configuration
=============

SFTP Connectors are configured at the company level, and are available in the
``res.company`` form inside of the ``SFTP Connectors`` page.

Usage
=====

Read Remote File
----------------

.. code-block:: python

   # sftp is a ``connector.sftp`` singleton.
   with sftp.open('path/to/remote/file') as file_handler:
       data = file_handler.read()

Write Remote File
-----------------

.. code-block:: python

   # sftp is a ``connector.sftp`` singleton.
   with sftp.open('path/to/remote/file', 'w') as file_handler:
       file_handler.write('Some data')

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

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

To contribute to this module, please visit https://odoo-community.org.
