.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=========================
Extra options in manifest
=========================

This is a technical module to allow developers to make use of a couple of new keys in module manifests.

The following new keys are available currently:

depends_if_installed
    Your module will depend on modules listed here, but only if those modules are already installed. This is useful if your module is supposed to override behavior of a third module if present, but it's not a hard dependency of your module. Think of auth_* and their interactions.

Usage
=====

* depend on this module and use the keys described above

Roadmap
=======

* ``breaks`` to mark some modules as being incompatible. This also could be versioned (``'breaks': ['my_module<<0.4.2']``)
* ``demo_if_installed``, ``data_if_installed``, ``qweb_if_installed`` being dicts with module names as keys and a list of files as values in order to pull some data files in case some other module is installed
* ``rdepends_if_installed`` to make another installed module depend on the current module
* ``_if_module`` on models to load certain models only if the appropriate module is installed

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

* Holger Brunn <hbrunn@therp.nl>

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

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
