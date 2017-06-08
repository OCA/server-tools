.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

=========================
Extended view inheritance
=========================

This module was written to make it simple to add custom operators for view
inheritance.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/149/8.0

Change a python dictionary (context for example)
------------------------------------------------

.. code-block:: xml

    <attribute name="$attribute" operation="python_dict" key="$key">
        $new_value
    </attribute>

Note that views are subject to evaluation of xmlids anyways, so if you need
to refer to some xmlid, say ``%(xmlid)s``.

Move an element in the view
---------------------------

.. code-block:: xml

    <xpath expr="$xpath" position="move" target="$targetxpath" />

This can also be used to wrap some element into another, create the target
element first, then move the node youwant to wrap there.

Add to values in a list (states for example)
--------------------------------------------

.. code-block:: xml

    <attribute name="$attribute" operation="list_add">
        $new_value(s)
    </attribute>

Remove values from a list (states for example)
----------------------------------------------

.. code-block:: xml

    <attribute name="$attribute" operation="list_remove">
        $remove_value(s)
    </attribute>

Known issues / Roadmap
======================

* add ``<attribute operation="json_dict" key="$key">$value</attribute>``
* support ``<xpath expr="$xpath" position="move" target="xpath" target_position="position" />``
* support an ``eval`` attribute for our new node types

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

* Odoo Community Association:
  `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Ronald Portier <rportier@therp.nl>

Do not contact contributors directly about help with questions or problems
concerning this addon, but use the
`community mailing list <mailto:community@mail.odoo.com>`_ or the
`appropriate specialized mailinglist <https://odoo-community.org/groups>`_
for help, and the bug tracker linked in `Bug Tracker`_ above for
technical issues.

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
