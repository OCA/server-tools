.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Date & Time Formatter
=====================

This module was written to extend the functionality of Odoo language engine to
support formatting `Date`, `Time` and `Datetime` fields easily and allow you to
print them in the best format for the user.

Usage
=====

This module adds a technical programming feature, and it should be used by
addon developers, not by end users. This means that you must not expect to see
any changes if you are a user and install this, but if you find you have it
already installed, it's probably because you have another modules that depend
on this one.

If you are a developer, to use this module, you need to:

* Call anywhere in your code::

    formatted_string = self.env["res.lang"].datetime_formatter(datetime_value)

* If you use Qweb::

    <t t-esc="env['res.lang'].datetime_formatter(datetime_value)"/>

* If you call it from a record that has a `lang` field::

    formatted_string = record.lang.datetime_formatter(record.datetime_field)

* ``models.ResLang.datetime_formatter`` docstring explains its usage.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/11.0

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

* Jairo Llopis <j.llopis@grupoesoc.es>
* Vicent Cubells <vicent.cubells@tecnativa.com>

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
