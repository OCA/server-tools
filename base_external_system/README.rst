.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl.html
   :alt: License: LGPL-3

======================
Base - External System
======================

This module provides an interface/adapter mechanism for the definition of remote
systems.

Note that this module stores everything in plain text. In the interest of security,
it is recommended you use another module (such as `keychain` or `red_october` to
encrypt things like the password and private key). This is not done here in order
to not force a specific security method.

Implementation
==============

The credentials for systems are stored in the ``external.system`` model, and are to
be configured by the user. This model is the unified interface for the underlying
adapters.

Using the Interface
-------------------

Given an ``external.system`` singleton called ``external_system``, you would do the
following to get the underlying system client:

.. code-block:: python

   with external_system.client() as client:
       client.do_something()

The client will be destroyed once the context has completed. Destruction takes place
in the adapter's ``external_destroy_client`` method.

The only unified aspect of this interface is the client connection itself. Other more
opinionated interface/adapter mechanisms can be implemented in other modules, such as
the file system interface in `OCA/server-tools/external_file_location
<https://github.com/OCA/server-tools/tree/9.0/external_file_location>`_.

Creating an Adapter
-------------------

Modules looking to add an external system adapter should inherit the
``external.system.adapter`` model and override the following methods:

* ``external_get_client``: Returns a usable client for the system
* ``external_destroy_client``: Destroy the connection, if applicable. Does not need
  to be defined if the connection destroys itself.

Configuration
=============

Configure external systems in Settings => Technical => External Systems

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/149/11.0

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
