.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============
Improved Search
===============

This module extends the search functionality to add simple shortcuts for
more complex search conditions.

Features:
* Fuzzy search: use wildcards ("%") in place of spaces


Installation
============

No specific requirements.


Configuration
=============

No specific setup needed.


Usage
=====

On any search box, in list or kanban views, type your expressions
and the magic will be automatically done.

For example, in a demo database, on the Contacts / Customers try searching
for "john brown". With this module installed will see the result
"John M. Brown", because of the fuzzy search feature.

At this moment the extensions are only applied for 'ilike' operations, the default used
by the search bar for text string fields.


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

.. repo_id is available in https://github.com/OCA/maintainer-tools/blob/master/tools/repos_with_ids.txt
.. branch is "8.0" for example

Known issues / Roadmap
======================

Additional serach tokens are welcome.

Some ideas:
* ".." for intervals
* Date tokens such as "t" for today


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/serevr-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Daniel Reis <https://github.com/dreispt>

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
