{
    "name": "GrayLog2 Handler",
    "version": "0.0.1",
    "author": ("Management and Accounting On-line, "
               "Odoo Community Association (OCA)"),
    "website": "https://github.com/OCA/server-tools/",
    "summary": "Provides ability to send log messages to graylog2 server",
    "category": "Added functionality",
    "description": """
.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=========================
GrayLog2 GELF log handler
=========================

This module provides ability to send log messages to graylog2 server.


Installation
============

To install this module, you need to:

* install *graypy* module in system (``pip install graypy``)


Configuration
=============

First, configure on your graylog2 server new input source of type *GELF UDP*
specifying port to make graylog listen to.

Next, you need to add folowing options in Your odoo configuration file::

    gelf_enabled: True                  ; enable graylog2 logging
    gelf_host: graylog.server.com       ; required, graylog2 host
    gelf_port: 12201                    ; required, graylog2 port
    gelf_localname: my.odoo.host        ; optional, use specified
                                        ; hostname as source host

where 12201 is port specified in first step.

Restart Odoo server and all log messages
additionaly will be sent to your graylog server


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue
has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed
feedback `here <https://github.com/OCA/server-tools/issues/new?\
body=module:%20graylog2_handler%0Aversion:%20{version}%0A\
%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20\
behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Dmytro Katyukha <firemage.dima@gmail.com>


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
    """,
    "depends": [
        'base',
    ],
    "active": True,
}
