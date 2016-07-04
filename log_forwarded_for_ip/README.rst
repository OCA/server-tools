.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

========================
Forwarded-for IPs in log
========================

This module makes werkzeug messages in the log show the IP the requests come from instead of the reverse proxy one.


Installation
============

Only install the module in the database.



Configuration
=============

You should be running Odoo with *--proxy-mode* or *proxy_mode = True* in your configuration file and have your reverse proxy set the XFF header.

This can be achieved with nginx adding the following in your site configuration:

    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;



Usage
=====

If everything is well configured, you will see the IPs the requests come from in the log instead of the proxy one.



Known issues / Roadmap
======================

* None


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
server-tools/issues/new?body=module:%20
log_forwarded_for_ip%0Aversion:%20
{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Pablo Cayuela <pablo.cayuela@aserti.es>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
