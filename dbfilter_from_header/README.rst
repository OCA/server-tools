.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
dbfilter_from_header
====================

This addon lets you pass a dbfilter as a HTTP header.

This is interesting for setups where database names can't be mapped to proxied host names.

Configuration
=============

In nginx, use one of:

* proxy_set_header X-OpenERP-dbfilter [your filter];
* proxy_set_header X-Odoo-dbfilter [your filter];

This addon has to be loaded as server-wide module.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
server-tools/issues/new?body=module:%20
dbfilter_from_header%0Aversion:%20
9.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Stéphane Bidoul <stephane.bidoul@acsone.eu>
* Yannick Vaucher <yannick.vaucher@camptocamp.com>
* Alexandre Fayolle <alexandre.fayolle@camptocamp.com>
* Holger Brunn <hbrunn@therp.nl>
* Laurent Mignon (aka lmi) <laurent.mignon@acsone.eu>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Fabio Vilchez <fabio.vilchez@clearcorp.co.cr>

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
