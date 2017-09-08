.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

===============================
Module Manifest - Extra Options
===============================

This is a technical module that allows developers to make use of extra keys in
module manifests. The following keys are available currently:

* ``depends_if_installed`` - Your module will depend on modules listed here but
  only if those modules are already installed. This is useful if your module is
  supposed to override the behavior of a certain module (dependencies determine
  load order) but does not need it to be installed.

Usage
=====

Add this module as a dependency and use the keys described above.

Roadmap
=======

Add support for the following additional keys:

* ``breaks`` - Used to mark some modules as being incompatible with the
  current one. This could be set up to support versioning (e.g. ``'breaks':
  ['my_module<<0.4.2']``).
* ``demo_if_installed``, ``data_if_installed``, ``qweb_if_installed`` - Dicts
  with module names as keys and lists of files as values. Used to load files
  only if some other module is installed.
* ``rdepends_if_installed`` - Similar to ``depends_if_installed`` but
  used to make another installed module depend on the current one.
* ``_if_module`` - Used on models to load them only if the appropriate module
  is installed.

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/OCA/server-tools/issues>`_. In case of
trouble, please check there if your issue has already been reported. If you
spotted it first, help us smash it by providing detailed and welcome feedback.

Credits
=======

Images
------

* Odoo Community Association:
  `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Oleg Bulkin <obulkin@laslabs.com>

Do not contact contributors directly about support or help with technical
issues.

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
