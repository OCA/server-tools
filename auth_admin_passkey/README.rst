.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
Auth Admin - Passkey
====================

This module extends the functionality of users module to support loging in with the administrator password
in other user accounts.

* Administrator has now the possibility to login in with any login;
* By default, Odoo will send a mail to user and admin to indicate them;
* If a user and the admin have the same password, admin will be informed;


Configuration
=============

To enable notifications for login attempts, you need to:

Go to Settings > General Settings.

Enable the "Send email to admin user" and / or "Send email to user" checkbox


Usage
=====

To login into a different user account type in the user name of the account and the password of the administrator at the login screen


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0


Known issues / Roadmap
======================

None

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

* Eugen Don <eugen.don@don-systems.de>
* Alexandre Papin (https://twitter.com/Fenkiou)
* Sylvain LE GAL (https://twitter.com/legalsylvain)


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
