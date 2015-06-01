.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

QWeb Usertime Tag
=================

This module adds a new tag renderer to QWeb, "usertime", which allows adding
the current time in the timezone of the user. It can be used as::

    <t t-usertime="%Y-%m-%d %H:%M:%S" />

or, if you want to use the default date and time formats based on the users
language::

    <t t-usertime="" />


Credits
=======

Contributors
------------

* Vincent Vinet <vincent.vinet@savoirfairelinux.com>

Maintainer
----------

.. image:: http://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: http://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.

