Email gateway - folders
=======================

Adds the possibility to attach emails from a certain IMAP folder to objects,
ie partners. Matching is done via several algorithms, ie email address, email
address's domain or the original Odoo algorithm.

This gives a simple possibility to archive emails in Odoo without a mail
client integration.

Configuration
=============

In your fetchmail configuration, you'll find a new list field `Folders to 
monitor`. Add your folders here in IMAP notation (usually something like
`INBOX.your_folder_name.your_subfolder_name`), choose a model to attach mails
to and a matching algorithm to use.

Exact mailaddress
-----------------

Fill in a field to search for the email address in `Field (model)`. For
partners, this would be `email`. Also fill in the header field from the email
to look at in `Field (email)`. If you want to match incoming mails from your
customers, this would be `from`. You can also list header fields, so to match
partners receiving this email, you might fill in `to,cc,bcc`.

Domain of email addresses
-------------------------

Match the domain of the email address(es) found in `Field (email)`. This would
attach a mail to `test1@example.com` to a record with `Field (model)` set to
`test2@example.com`. Given that this is a fuzzy match, you probably want to
check `Use 1st match`, because otherwise nothing happens if multiple possible
matches are found.

Odoo standard
-------------

This is stricly speaking no matching algorithm, but calls the model's standard
action on new incoming mail, which is usually creating a new record.

Usage
=====

A widespread configuration is to have a shared mailbox with several folders,
i.e. one where users drop mails they want to attach to partners. Let this
folder be called `From partners`. Then create a folder configuration for your
server with path `"INBOX.From partners"` (note the quotes because of the space,
this is server dependent). Choose model `Partners`, set `Field (model)` to
`email` and `Field (email)` to `from`. In `Domain`, you could fill in
`[('customer', '=', True)]` to be sure to only match customer records.

Now when your users drop mails into this folder, they will be fetched by Odoo
and attached to the partner in question. After some testing, you might want to
check `Delete matches` in your folder configuration so that this folder doesn't
grow indefinitely.

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
