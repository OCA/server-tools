.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
JSON Logging
==============

This addon allows to output the Odoo logs in JSON.


Configuration
=============

The json logging is activated with the environment variable
``ODOO_LOGGING_JSON`` set to ``1``.

In order to have the logs from the start of the server, you should add
``logging_json`` in the ``--load`` flag or in the ``server_wide_modules``
option in the configuration file.
To configure this module, you need to:

Known issues / Roadmap
======================

* Completed the extraction (in regex) of interesting message to get more metric

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

* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Sébastien BEAU <sebastien.beau@akretion.com>

Funders
-------

The development of this module has been financially supported by:

* Camptocamp
* Akretion

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
