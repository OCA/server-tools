.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============
Mass Sorting
============

This module extends the functionality of odoo to allow users to sort an
one2many fields in any model.

Typically, you can sort sale order lines on a sale order, using any fields.

Configuration
=============

To configure this module, you need to:

* Go to Settings / Technical / Mass Sorting

* Create a new item and define:
    * a name
    * the model you want to sort
    * the field of the model, you want to sort
    * The lists of the fields, by which the sort will be done

.. image:: /mass_sorting/static/description/1_mass_sort_config.png
   :width: 70%

(You can allow users to change or not the values, by checking 'Allow custom Setting')

*  Click on the button 'Add sidebar button'

Usage
=====

* Go to the form view of the given model, in this sample, a sale order. (or select items in a tree view)

.. image:: /mass_sorting/static/description/4_before.png

* click on the button 'Action' and then select the according action

.. image:: /mass_sorting/static/description/2_button.png

* On the pop up (depending of the configuration), change the fields and the order

.. image:: /mass_sorting/static/description/3_mass_sort_wizard_custom.png

(If changing configuration is not allowed, a simple message is displayed.)

.. image:: /mass_sorting/static/description/3_mass_sort_wizard.png

* The items will be reordered.

.. image:: /mass_sorting/static/description/5_after.png


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/10.0

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

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Funders
-------

The development of this module has been financially supported by:

* GRAP (http://www.grap.coop)

This module is highly inspired by 'mass_editing' module. (by OCA and SerpentCS)

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

