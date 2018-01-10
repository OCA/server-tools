.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
Analytic Structure
==================

This module allows to use several analytic dimensions through a structure
related to an object model.

Configuration
=============

In your OpenERP server's configuration file, you can set several optional
parameters related to the analytic module::

    [analytic]
    key = value ...


Those options must be grouped under the [analytic] category. If the category
doesn't exist, add it to your configuration file.

analytic_size (default: 5)
    define the maximum number of analytic dimensions that can be associated
    with a model.

translate (default: False)
    enable or disable the translation of field values on analytic dimensions
    (name) and codes (name and description).

Usage
=====

Add the MetaAnalytic metaclass to a model
-----------------------------------------

At the beginning of the source file, import the MetaAnalytic metaclass::

    from openerp.addons.analytic_structure.MetaAnalytic import MetaAnalytic

Inside your Model class, define MetaAnalytic to be used as metaclass::

    __metaclass__ = MetaAnalytic


Add analytic fields to a model
------------------------------

First of all, make sure you are using the MetaAnalytic metaclass.
Then, add the _analytic attribute to your class, using the following syntax.

A) Use the analytic fields associated with the model::

    _analytic = True


B) Use analytic fields associated with another model::

    _analytic = 'account_move_line'


C) Use several analytic field structures, associated with different prefixes::

    _analytic = {
        'a': 'account_asset_asset',
        't': 'account_move_line',
    }


Add analytic fields to a view
-----------------------------

Analytic fields can be added to the view individually, like any other field::

    <field name="a1_id" />

'a' is the prefix associated with the structure. By default, it is 'a'.
'1' is the dimension's ordering as defined by the analytic structure.

You can also use a field named 'analytic_dimensions' to insert every analytic
field within a given structure (defined by its prefix) that wasn't explicitly
placed in the view. This field is automatically generated when you call
the Metaclass::

    <field name="analytic_dimensions" required="1" prefix="t" />

The prefix can be omitted for a structure that uses the default prefix 'a'.
Any other attribute will be propagated to the analytic fields.

Warning: analytic fields should generally not be used inside nested sub-views.
If possible, create a separate record and use the context to specify the view::

    <field name="order_line" colspan="4" nolabel="1" context="{
        'form_view_ref' : 'module.view_id',
        'tree_view_ref' : 'module.view_id'
    }"/>



Bind an analytic dimension to a model
-------------------------------------

First of all, make sure you are using the MetaAnalytic metaclass.
Then, add the _dimension attribute to your class, using the following syntax.

A) Bind the model to a new analytic dimension named after the model,
   using default values::

    _dimension = True


B) Bind the model to a new analytic dimension with a specified name,
   using default values::

    _dimension = 'Funding Source'


C) Bind the model to a new or existing analytic dimension,
   using either custom or default values::

    _dimension = {
        'name': 'School',
        'column': 'analytic_code_id',
        'ref_id': 'school_analytic_dimension',
        'ref_module': 'my_module',
        'sync_parent': False,
        'rel_description': True,
        'rel_active': (u"Active", 'active_code'),
        'use_inherits': False,
        'use_code_name_methods': False,
    }



name (default: value of the model's _description or _name field)
    The name of the analytic dimension.
    This name is only used when creating the dimension in the database.

column (default: analytic_id)
    The field that links each record to an analytic code.

ref_id (default: value of the model's _name field + analytic_dimension_id)
    The external ID that will be used by the analytic dimension. By setting
    this value, you can allow two models to use the same dimension,
    or a model to use an already existing one.

ref_module (default: empty string)
    The name of the module associated with the dimension record. Change this
    value in order to use a dimension defined in a data file.

sync_parent (default: False)
    Controls the synchronization of the codes' parent-child
    hierarchy with that of the model. When using an inherited, rename dparent
    field, you must give the parent field name rather than simply True.

use_inherits (default: True or False, special)
    Determines whether the analytic codes should be bound to the records by
    inheritance, or through a simple many2one field.
    Inheritance allows for better synchronization, but can only be used if
    there are no duplicate fields between the two objects.
    The default value is True if the model has no 'name' and 'code_parent_id'
    field as well as no inheritance of any kind, and False otherwise. If the
    object's inheritances do not cause any conflict, you can set it to True.

rel_active (default: False)
    Create a related field in the model, targeting the analytic code field
    'active' and with an appropriate store parameter.
    This is useful when the model doesn't inherit analytic_code and/or when it
    already has a field named 'active'.
    Can take a pair of string values: (field label, field name).
    If given a string, the default field name 'active' will be used.
    If given True, the default field label 'Active' will also be used.

rel_description (default: False)
    Same as rel_active for the code field 'description'.
    If given a string, the default field name 'description' will be used.
    If given True, the default field label 'Description' will also be used.

use_code_name_methods (default: False)
    Set to True in order to override the methods name_get and name_search,
    using those of analytic code.
    This allows the analytic code's description to be displayed (and searched)
    along with the entry's name in many2one fields targeting the model.


Active / View type / Disabled in my company
-------------------------------------------

Differences between the various "active" fields:

- Active: Determines whether an analytic code is in the referential.

- View type: Determines whether an analytic code is not selectable
  (but still in the referential).

- Disabled per company: Determines whether an analytic code is disabled
  for the current company.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/
server-tools/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback `here <https://github.com/OCA/
server-tools/issues/new?body=module:%20
analytic_structure%0Aversion:%20
2.0.1%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Alexandre Allouche <alexandre.allouche@xcg-consulting.fr>
* Anael Lorimier <anael.lorimier@xcg-consulting.fr>
* Nicolas He <nicolas.he@xcg-consulting.fr>
* Florent Aide <florent.aide@gmail.com>
* Jérémie Gavrel <jeremie.gavrel@xcg-consulting.fr>
* Alexandre Brun <alexandre.brun@xcg-consulting.fr>
* Vincent Hatakeyama <vincent.hatakeyama@xcg-consulting.fr>
* Matthieu Gautier <matthieu.gautier@mgautier.fr>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
