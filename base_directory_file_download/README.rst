.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

========================
Directory Files Download
========================

View and download the files contained in a directory on the server.

This functionality can have impacts on the security of your system,
since it allows to download the content of a directory.
Be careful when choosing the directory!

Notice that, for security reasons, files like symbolic links
and up-level references are ignored.


Configuration
=============

To configure this module, you need to:

#. Set the group "Download files of directory" for the users who need this functionality.


Usage
=====

To use this module, you need to:

#. Go to Settings -> Downloads -> Directory Content
#. Create a record specifying Name and Directory of the server
#. Save; a list of files contained in the selected directory is displayed
#. Download the file you need
#. In case the content of the directory is modified, refresh the list by clicking the button on the top-right of the form


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

* Andrea Stirpe <a.stirpe@onestein.nl>

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
