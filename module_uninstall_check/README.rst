.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

============================
Module Uninstallation Checks
============================

This module extends the functionality of base module, to improve modules
uninstallation process.

It provides an extra view, on module form to display which models (SQL tables)
and which fields (SQL columns) will be dropped, if the selected module is
uninstalled.


Usage
=====

To use this module, you need to:

#. Go to Settings / Modules / Local Modules
#. Select an installed module
#. Click on the button 'Uninstallation Impact'

.. figure:: ./module_uninstall_check/static/description/module_form.png
   :width: 800 px

* Sample, selecting sale_margin module

.. figure:: ./module_uninstall_check/static/description/sale_margin_uninstallation.png
   :width: 800 px

* Sample, selecting sale_stock module, when sale_margin is installed

.. figure:: ./module_uninstall_check/static/description/sale_uninstallation.png
   :width: 800 px

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/8.0

Known issues / Roadmap
======================

* In some cases, we want to uninstall a module, but prevent some data deletion.
  This can happen:
    * if we want to keep backup some datas;
    * if the data moved into another module after a refactoring;

This module could implement such feature, adding extra feature on wizard lines,
deleting or renaming xml ids.

* For the time being, wizard displays size used for models in database. It
  could be interesting to know the space released by the deletion of a column.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Sylvain LE GAL (https://twitter.com/legalsylvain)

Funders
-------

The development of this module has been financially supported by:

* GRAP, Groupement Régional Alimentaire de Proximité (http://www.grap.coop)

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

