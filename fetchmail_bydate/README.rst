.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

================
Fetchmail Bydate
================

This module allows to fetch new emails (using IMAP) received from the last
time they were downloaded and successfully processed, in addition to 'unseen'
status.

Users with authorization to edit the email server in Odoo can introduce a
new date and time to download from.

In case of errors found during the processing of an email Odoo will
re-attempt to fetch the emails from the last date and time they were
successfully received and processed.



Configuration
=============

To enable this, you have to set a 'Last Download Date' in the fetchmail.server
After that, emails with an internal date greater than the saved one will be
downloaded.


Usage
=====

Odoo will attempt to fetch emails starting from the 'Last Download Date'
defined in the email server. If all mails have been processed successfully,
it will update this date with the latest message received.

System administrators need to be attentive to the Odoo logs, looking for errors
raised during the processing of emails, in order to avoid situations where
lots of emails are downloaded and reprocessed every time, due to errors found
 in a few old emails that were unattended.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0


Known issues / Roadmap
======================

* This module should not be used together with the OCA module
  `fetchmail_notify_error_to_sender <https://github.com/OCA/server-tools/tree/9
  .0/fetchmail_notify_error_to_sender>`_, because this other module sends an
  email to the author of an email when it could not be processed. And you
  would be spamming to the original authors every time Odoo tries to
  re-process the email.

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

* Lorenzo Battistini <lorenzo.battistini@agilebg.com>
* Alessio Gerace
* Jordi Ballester <jordi.ballester@eficent.com>


Do not contact contributors directly about support or help with technical issues.


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
