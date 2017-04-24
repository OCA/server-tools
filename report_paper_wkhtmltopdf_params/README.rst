.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===============================
Report Paper Wkhtmltopdf Params
===============================

This module allows you to add new parameters for a paper format which are
then forwarded to wkhtmltopdf command as arguments. To display the arguments
that wkhtmltopdf accepts go to your command line and type 'wkhtmltopdf -H'.

A commonly used parameter in Odoo is *--disable-smart-shrinking*, that will
disable the automatic resizing of the PDF when converting. This is
important when you intend to have a layout that conforms to certain alignment.
It is very common whenever you need to conform the PDF to a predefined
layoyut (e.g. checks, official forms,...).


Usage
=====

# Go to *Settings* and press 'Activate the developer mode (with assets)'

# Go to *Settings - Technical - Reports - Paper Format*

# Change the parameter 'Disable Smart Shrinking'.

# Add additional parameters indicating the command argument name (remember to
  add prefix -- or -) and value.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0


Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Miku Laitinen <miku@avoin.systems>
* Jordi Ballester <jordi.ballester@eficent.com>


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
