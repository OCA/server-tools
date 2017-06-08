.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

========================
QWeb for email templates
========================

This module was written to allow you to write email templates in QWeb instead
of jinja2. The advantage here is that with QWeb, you can make use of
inheritance and the ``call`` statement, which allows you to reuse designs and
snippets in multiple templates, making your development process simpler.

Usage
=====

To use this module, you need to:

* Select `QWeb` in the field `Body templating engine`
* Select a QWeb view to be used to render the body field
* Apart from QWeb's standard variables, you also have access to ``object`` and
  ``email_template``, which are browse records of the current object and the
  email template in use, respectively.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

Demo data contains an example on how to separate corporate identity from a
template's content.

For further information, please visit:

* https://www.odoo.com/forum/help-1

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20email_template_qweb%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>

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
