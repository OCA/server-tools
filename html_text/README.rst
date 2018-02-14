.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

====================
Text from HTML field
====================

This module provides some technical features that allow to extract text from
any chunk of HTML, without HTML tags or attributes. You can chose either:

* To truncate the result by amount of words or characters.
* To append an ellipsis (or any character(s)) at the end of the result.

It can be used to easily generate excerpts.

Usage
=====

This module just adds a technical utility, but nothing for the end user.

If you are a developer and need this utility for your module, see these
examples and read the docs inside the code.

Python example::

    @api.multi
    def some_method(self):
        # Get truncated text from an HTML field. It will 40 words and 100
        # characters at most, and will have "..." appended at the end if it
        # gets truncated.
        truncated_text = self.env["ir.fields.converter"].text_from_html(
            self.html_field, 40, 100, "...")

QWeb example::

    <t t-esc="env['ir.fields.converter'].text_from_html(doc.html_field)"/>

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/11.0

Known issues / Roadmap
======================

* An option could be added to try to respect the basic HTML tags inside the
  excerpt (``<b>``, ``<i>``, ``<p>``, etc.).

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

* Jairo Llopis <yajo.sk8@gmail.com>
* Vicent Cubells <vicent.cubells@tecnativa.com>
* Dennis Sluijk <d.sluijk@onestein.nl>

Do not contact contributors directly about support or help with technical issues.

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
