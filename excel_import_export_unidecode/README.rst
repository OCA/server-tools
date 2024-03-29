=====================================
Excel Import/Export/Report: Unidecode
=====================================

.. 
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! source digest: sha256:822082434faf27c0d380390ffab4662760465d6a6de58c8a15d9f98b09b2e3c9
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-OCA%2Fserver--tools-lightgray.png?logo=github
    :target: https://github.com/OCA/server-tools/tree/16.0/excel_import_export_unidecode
    :alt: OCA/server-tools
.. |badge4| image:: https://img.shields.io/badge/weblate-Translate%20me-F47D42.png
    :target: https://translation.odoo-community.org/projects/server-tools-16-0/server-tools-16-0-excel_import_export_unidecode
    :alt: Translate me on Weblate
.. |badge5| image:: https://img.shields.io/badge/runboat-Try%20me-875A7B.png
    :target: https://runboat.odoo-community.org/builds?repo=OCA/server-tools&target_branch=16.0
    :alt: Try me on Runboat

|badge1| |badge2| |badge3| |badge4| |badge5|

This module adds the extra unidecode option to be applied to the exported data. Example: e.g. ESPAÑA to ESPANA or forçut to forcut.

**Table of contents**

.. contents::
   :local:

Installation
============

To install this module, you need to install following python library, **unidecode**.

Usage
=====

To apply unidecode just check the Unidecode field for the data where you want to apply it in the Excel template.
If you are defining the template you only have to specify @?unidecode? e.g. 'A2': 'picking_id.export_reference${value or ""}@?unidecode?'

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us to smash it by providing a detailed and welcomed
`feedback <https://github.com/OCA/server-tools/issues/new?body=module:%20excel_import_export_unidecode%0Aversion:%2016.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Do not contact contributors directly about support or help with technical issues.

Credits
=======

Authors
~~~~~~~

* FactorLibre

Contributors
~~~~~~~~~~~~

* Rodrigo Bonilla. <rodrigo.bonilla@factorlibre.com> (https://factorlibre.com/)

Maintainers
~~~~~~~~~~~

This module is maintained by the OCA.

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

This module is part of the `OCA/server-tools <https://github.com/OCA/server-tools/tree/16.0/excel_import_export_unidecode>`_ project on GitHub.

You are welcome to contribute. To learn how please visit https://odoo-community.org/page/Contribute.
