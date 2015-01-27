Email gateway - folders
=======================

Adds the possibility to attach emails from a certain IMAP folder to objects,
ie partners. Matching is done via several algorithms, ie email address, email
address's domain or the original Odoo algorithm.

This gives a simple possibility to archive emails in Odoo without a mail
client integration.

Configuration
=============

In your fetchmail configuration, you'll find a new field `folders`. Add your
folders here in IMAP notation [TODO]

Usage
=====

A widespread configuration is to have a shared mailbox with several folders [TODO]

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

Icon
----

http://commons.wikimedia.org/wiki/File:Crystal_Clear_filesystem_folder_favorites.png

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
