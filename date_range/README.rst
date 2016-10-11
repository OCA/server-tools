.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========
Date Range
==========

This module lets you define global date ranges that can be used to filter
your values in tree views.

Usage
=====

To configure this module, you need to:

* Go to Settings > Technical > Date ranges > Date Range Types where
  you can create types of date ranges.

  .. figure:: static/description/date_range_type_create.png
     :scale: 80 %
     :alt: Create a type of date range

* Go to Settings > Technical > Date ranges >  Date Ranges where
  you can create date ranges.
  
  .. figure:: static/description/date_range_create.png
     :scale: 80 %
     :alt: Date range creation
  
  It's also possible to launch a wizard from the 'Generate Date Ranges' menu.

  .. figure:: static/description/date_range_wizard.png
     :scale: 80 %
     :alt: Date range wizard

  The wizard is useful to generate recurring periods.
  
  .. figure:: static/description/date_range_wizard_result.png
     :scale: 80 %
     :alt: Date range wizard result

* Your date ranges are now available in the search filter for any date or datetime fields

  Date range types are proposed as a filter operator
  
  .. figure:: static/description/date_range_type_as_filter.png
     :scale: 80 %
     :alt: Date range type available as filter operator

  Once a type is selected, date ranges of this type are porposed as a filter value

  .. figure:: static/description/date_range_as_filter.png
     :scale: 80 %
     :alt: Date range as filter value

  And the dates specified into the date range are used to filter your result.
  
  .. figure:: static/description/date_range_as_filter_result.png
     :scale: 80 %
     :alt: Date range as filter result


.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/10.0


Known issues / Roadmap
======================

* The addon use the daterange method from postgres. This method is supported as of postgresql 9.2

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

* Laurent Mignon <laurent.mignon@acsone.eu>

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
