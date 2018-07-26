.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

====================
dbfilter_from_header
====================

This addon lets you pass a dbfilter as a HTTP header.

This is interesting for setups where database names can't be mapped to proxied host names.

Installation
============

To install this module, you only need to add it to your addons, and load it as
a server-wide module.

This can be done with the ``server_wide_modules`` parameter in ``/etc/odoo.conf``
or with the ``--load`` command-line parameter

``server_wide_modules = "web, dbfilter_from_header"``

Configuration
=============

Please keep in mind that the standard odoo dbfilter configuration is still
applied before looking at the regular expression in the header.

* For nginx, use:

  ``proxy_set_header X-Odoo-dbfilter [your filter regex];``

* For caddy, use:

  ``proxy_header X-Odoo-dbfilter [your filter regex]``

* For Apache, use:

  ``RequestHeader set X-Odoo-dbfilter [your filter regex]``

And make sure that proxy mode is enabled in Odoo's configuration file:

``proxy_mode = True``

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

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
* Jos De Graeve <Jos.DeGraeve@apertoso.be>
* Lai Tim Siu (Quaritle Limited) <info@quartile.co>

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
