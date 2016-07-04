.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=======================
PDF Compression & PDF/A
=======================

This addon provides the ability to convert outgoing and imported PDF attachments.
You can compress the PDFs to save space in you database or file system.
Also the possibility exists to convert PDFs in PDF/A. Currently implemented:

* PDF/A-1b
* PDF/A-2b (recommend to use this setting because it is faster and result in smaller files)


Installation
============

#. You need at least Gostscript 9.18 (I recommend 9.19)
   `http://ghostscript.com <http://ghostscript.com/download/gsdnld.html>`_


Configuration
=============

If the odoo module is installed:

#. You can define ``Compession level`` and ``PDF/A TYPE`` via
   `Settings -> Configuration -> Knowledge`.
#. Also you can override PDF/A option for individual Reports apart from Global Settings via
   `Settings -> Technical -> Reports -> Reports -> Select a Report -> PDF/A archiving`.



Usage
=====


#. Compression rate outcome:

   I uploaded a 1MB PDF file with a mix of pictures tables and text.

   Settings:

   * screen: selects low-resolution output similar to the Acrobat Distiller "Screen Optimized" setting.
   * ebook: selects medium-resolution output similar to the Acrobat Distiller "eBook" setting.
   * printer: selects output similar to the Acrobat Distiller "Print Optimized" setting.
   * prepress: selects output similar to Acrobat Distiller "Prepress Optimized" setting.
   * default: selects output intended to be useful across a wide variety of uses, possibly at the expense of a larger output file.

   Examples:

   * screen: 1MB -> 200KB some quality loss notice (jpg artefacts in pictures)
   * ebook: 1MB -> 540KB little quality loss notice (some jpg artefacts in pictures but way better then screen)
   * printer: 1MB -> 740KB no quality loss notice
   * prepress: 1MB -> 820KB  no quality loss notice
   * default: 1MB -> 680KB  little quality loss notice (some jpg artefacts in pictures but way better then screen)

#. PDF/A conversion:

   `Info wiki page <https://en.wikipedia.org/wiki/PDF/A>`_

   PDFs will be converted to:

   * PDF/A-1b
   * PDF/A-2b



Known issues / Roadmap
======================

* Had to override the _run_wkhtmltopdf Function to pass context through it
* Implementing other PDF/A options
* Future Goal to integrate ZUGFeRD
* only PDFs which are saved as attachments are converted
* (if you use the print button to generate pdf the "first" time the compession/pdfa is not used but the saved attachment is converted)


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

* Benjamin Bachmann <https://github.com/Benniphx>

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
