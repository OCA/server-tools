.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=======================
Custom domain operators
=======================

This module was written to allow developers to define custom domain operators. This can be very helpful for complicated selections or ir.rules.

Currently implemented operators
===============================

``parent_of``
  The inverse of ``child_of``: Searches for the parents of given records in the hierarchy, including the records themselves::

    [('id', 'parent_of', [42])]

Usage
=====

To use this module, you need to:

#. depend on it
#. use one of the operators explained above in any of your domains

To add your own operators:

#. in ``base.domain.operator``, define a function ``_operator_${your_operator}`` with decorator ``@api.model`` and signature ``leaf, expression``
#. ``leaf`` is a 3-tuple of a domain proposition, ``expression`` an instance of ``openerp.osv.expression.expression``
#. return a list of ``openerp.osv.expression.ExtendedLeaf`` instances that maps your operator to some expressions the original domain parser can evaluate
#. note that you can use the internal ``inselect`` operator here if you pass ``internal=True`` to ``ExtendedLeaf``'s constructor
#. be careful with using the ORM in those handlers to avoid infinite loops
#. take good care that you don't introduce SQL injections and other security problems

Known issues / Roadmap
======================

* given the upstream code is not exactly extension friendly, we'll have to reimplement a bunch of helper functions
* ``parent_of`` currently doesn't support dotted paths and searching for names (``name_get``), this needs to be amended as needed
* another nice operator would be ``indomain``, probably also with a way to refer to the table's columns in the right hand side of expressions

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
