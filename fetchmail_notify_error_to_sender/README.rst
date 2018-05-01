.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================================
Fetchmail Notify Error to Sender
================================

If fetchmail is not able to correctly route an email, the email is
"silently" lost (you get an error message in server log).

For example, if you configure odoo mail system to route received emails
according to recipient address, it may happen users send emails to wrong
email address.

This module extends the functionality of fetchmail to allow you to
automatically send a notification email to sender, when odoo can't
correctly process the received email.


Configuration
=============

To configure this module, you need to:

#. Configure your fetchmail server setting 'Error notice template' = 'Fetchmail - error notice'.
#. You can edit the 'Fetchmail - error notice' email template according to your needs.

.. figure:: path/to/local/image.png
   :alt: alternative description
   :width: 600 px

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

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
* Miquel Raïch <miquel.raich@eficent.com> (migration to v9 and v10)
* Hai Dinh <haidd.uit@gmail.com> (migration to V11)

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