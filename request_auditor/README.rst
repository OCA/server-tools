.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===============
request_auditor
===============

Creates a separate log for auditing the user actions. Can be configured to
log to any handler accepted by Python's logging (file, logstash, etc) in any
format.

Configuration
=============

In Odoo's configuration file, add the ``audit_log`` section. The keys are the
same as in Python's logging handler configuration, plus three extra (optional):

   - ``format``: log format as used by Python's ``logging``
   - ``formatter_class``: complete path of a Formatter class
   - ``filter_methods``: Odoo Request methods to be logged, separated by commas. Default: ``call,call_kw,call_button``

Example::

    [audit_log]
    class = logging.FileHandler
    filename = /tmp/audit.log
    formatter_class = pythonjsonlogger.jsonlogger.JsonFormatter

Credits
=======

Contributors
------------

* André Paramés Pereira <github@andreparames.com>

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* ACSONE SA/NV

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
