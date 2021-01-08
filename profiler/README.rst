.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============
Odoo Profiler
=============

Integration of python cprofile and postgresql logging collector for Odoo
Check the Profiler menu in admin menu

Installation
============

To make use of the Postgres capabilities, enable Postgres logging and install PGbadger.

Python profiling will work out of the box.

Usage
=====

For Python profiling we have two methods:

**Full profiling**: Profile anything that happens between A and B. For this method, start Odoo
with workers=0, create a profile record and select Python method 'All activity'. Enable
the profiler, do actions in Odoo, and disable again. Under 'Attachments' you can download the
cProfile stats file.

**Profile current session per HTTP request**: Profile HTTP requests in the active user session.
This method also works in multi-worker mode. Create a profile record and select Python method
'Per HTTP request'. Enable the profiler, do actions in Odoo, and see the list filling up with
requests. After some time, disable. You can find your slow HTTP requests by sorting
on the 'Total time' column, and download the cProfile stats file for further analysis.

Stats files can be analyzed visually for example with Snakeviz or Tuna.

Credits
=======

Contributors
------------

* Moisés López <moylop260@vauxoo.com>
* Tom Blauwendraat <tom@sunflowerweb.nl>

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
