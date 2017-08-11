.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3

====================
Locale - Default UoM
====================

This module adds a concept of a default unit of measure on languages, unique by
unit category type.

It also provides a method that can be used in fields to work from said defaults.

Configuration
=============

Set default unit of measures in the `Languages` menu in settings.

Usage
=====

Fields that want to implement the language default should use the provided method,
such as in the below example::

   class MyModel(models.Model):
       _name = 'my.model'
       time_uom_id = fields.Many2one(
           string='Time Units',
           comodel_name='product.uom',
           default=lambda s: s.env['res.lang'].default_uom_by_category('Time'),
       )

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/9.0

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

* Dave Lasley <dave@laslabs.com>

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
