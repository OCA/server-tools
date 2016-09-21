.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===
KPI
===

This module provides the basis for creating key performance indicators,
including static and dynamic thresholds (SQL query or Python code),
on local and remote data sources.

The module also provides the mecanism to update KPIs automatically.
A scheduler is executed every hour and updates the KPI values, based
on the periodicity of each KPI. KPI computation can also be done
manually.

A threshold is a list of ranges and a range is:

* a name (like Good, Warning, Bad)
* a minimum value (fixed, sql query or python code)
* a maximum value (fixed, sql query or python code)
* color (RGB code like #00FF00 for green, #FFA500 for orange, #FF0000 for red)

Configuration
=============

Users must be added to the appropriate groups within Odoo as follows:
* Creators: Settings > Users > Groups > Management System / User
* Responsible Persons: Settings > Users > Groups > Management System / Approving User

Usage
=====

https://www.youtube.com/watch?v=OC4-y2klzIk

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/128/9.0

Known issues / Roadmap
======================

* Use web_widget_color to display color associated to threshold range

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.

Credits
=======

Contributors
------------

* Daniel Reis <dreis.pt@hotmail.com>
* Glen Dromgoole <gdromgoole@tier1engineering.com>
* Loic Lacroix <loic.lacroix@savoirfairelinux.com>
* Sandy Carter <sandy.carter@savoirfairelinux.com>
* Gervais Naoussi <gervaisnaoussi@gmail.com>

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
