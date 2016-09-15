.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
    :alt: License: LGPL-3

================
Base Custom Info
================

This module allows you to attach custom information to records without the need
to alter the database structure too much.

Definitions
===========

This module defines several concepts that you have to understand.

Templates
---------

A *template* is a collection of *properties* that a record should have.
*Templates* always apply to a given model, and then you can choose among the
current templates for the model you are using when you edit a record of that
model.

I.e., This addon includes a demo template called "Smart partners", that applies
to the model ``res.partner``, so if you edit any partner, you can choose that
template and get its properties autofilled.

Properties
----------

A *property* is the "name" of the field. *Templates* can have any amount of
*properties*, and when you apply a *template* to a record, it automatically
gets all of its *properties* filled, empty (unless they have a *Default
value*), ready to assign *values*.

You can set a property to as *required* to force it have a value, although you
should keep in mind that for yes/no properties, this would mean that only *yes*
can be selected, and for numeric properties, zero would be forbidden.

Also you can set *Minimum* and *Maximum* limits for every *property*, but those
limits are only used when the data type is text (to constrain its length) or
number. To skip this constraint, just set a maximum smaller than the minimum.

*Properties* always belong to a template, and as such, to a model.

*Properties* define the data type (text, number, yes/no...), and when the type
is "Selection", then you can define what *options* are available.

I.e., the "Smart partners" *template* has the following *properties*:

- Name of his/her teacher
- Amount of people that hates him/her for being so smart
- Average note on all subjects
- Does he/she believe he/she is the smartest person on earth?
- What weaknesses does he/she have?

When you set that template to any partner, you will then be able to fill these
*properties* with *values*.

Categories
----------

*Properties* can also belong to a *category*, which allows you to sort them in
a logical way, and makes further development easier.

For example, the ``website_sale_custom_info`` addon uses these to display a
technical datasheet per product in your online shop, sorted and separated by
category.

You are not required to give a *category* to every *property*.

Options
-------

When a *property*'s type is "Selection", then you define the *options*
available, so the *value* must be one of these *options*.

I.e., the "What weaknesses does he/she have?" *property* has some options:

- Loves junk food
- Needs videogames
- Huge glasses

The *value* will always be one of these.

Recursive templates using options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Oh dear customization lovers! Options can be used to customize the custom
information template!

.. figure:: /base_custom_info/static/description/customizations-everywhere.jpg
   :alt: Customizations Everywhere

If you assign an *additional template* to an option, and while using the owner
form you choose that option, you can then press *reload custom information
templates* to make the owner update itself to include all the properties in all
the involved templates. If you do not press the button, anyway the reloading
will be performed when saving the owner record.

.. figure:: /base_custom_info/static/description/templateception.jpg
   :alt: Templateception

I.e., if you select the option "Needs videogames" for the property "What
weaknesses does he/she have?" of a smart partner and press *reload custom
information templates*, you will get 2 new properties to fill: "Favourite
videogames genre" and "Favourite videogame".

Value
-----

When you assign a *template* to a partner, and then you get the *properties* it
should have, you still have to set a *value* for each property.

*Values* can be of different types (whole numbers, constrained selection,
booleans...), depending on how the *property* was defined. However, there is
always the ``value`` field, that is a text string, and converts automatically
to/from the correct type.

Why would I need this?
~~~~~~~~~~~~~~~~~~~~~~

Imagine you have some partners that are foreign, and that for those partners
you need some extra information that is not needed for others, and you do not
want to fill the partners model with a lot of fields that will be empty most of
the time.

In this case, you could define a *template* called "Foreign partners", which
will be applied to ``res.partner`` objects, and defines some *properties* that
these are expected to have.

Then you could assign that *template* to a partner, and automatically you will
get a subtable of all the properties it should have, with tools to fill their
*values* correctly.

Does this work with any model?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Yes and no.

Yes, because this is a base module that provides the tools to make this work
with any model.

No, because, although the tools are provided, they are only applied to the
``res.partner`` model. This is by design, because different models can have
different needs, and we don't want to depend on every possible model.

So, if you want to apply this to other models, you will have to develop a
little additional addon that depends on this one. If you are a developer, refer
to the *Development* section below.

Installation
============

This module serves as a base for other modules that implement this behavior in
concrete models.

This module is a technical dependency and is to be installed in parallel to
other modules.

Configuration
=============

To enable the main *Custom Info* menu:

#. Enable *Settings > General Settings > Manage custom information*.

To enable partner's custom info tab:

#. Enable *Settings > General Settings > Edit custom information in partners*.

Usage
=====

This module defines *Custom Info Templates* that define what properties are
expected for a given record.

To define a template, you need to:

* Go to *Custom Info > Templates*.
* Create one.
* Add some *Properties* to it.

All database records with that template enabled will automatically fill those
properties.

To manage the properties, you need to:

* Go to *Custom Info > Properties*.

To manage the property categories, you need to:

* Go to *Custom Info > Categories*.

Some properties can have a number of options to choose, to manage them:

* Go to *Custom Info > Options*.

To manage their values, you need to:

* Go to *Custom Info > Values*.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/135/9.0

Development
===========

To create a module that supports custom information, just depend on this module
and inherit from the ``custom.info`` model.

See an example in the ``product_custom_info`` addon.

Known issues / Roadmap
======================

* Custom properties cannot be shared among templates.
* You get an error if you press *Save & New* when setting property values in
  partner form.
* You have to press *reload custom information templates*, when the optimal
  thing would be the reloading taking place whenever needed: when you change
  the template, or when you choose an option that has an additional template.
  However, `currently it is impossible for a x2many field to update itself
  <https://github.com/odoo/odoo/issues/2693#issuecomment-56825399>`_, and it is
  needed to skip some checks when you are saving a record after filling the
  templates, which has to be done by `changing the context, something also not
  possible currently at onchange time
  <https://github.com/odoo/odoo/issues/7472>`_. So there are some technical
  limitations that do not let us reach the ideal UX for this addon. So, in
  short, press the button when you see it and be happy.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/product-attribute/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Rafael Blasco <rafabn@antiun.com>
* Carlos Dauden <carlos@incaser.es>
* Sergio Teruel <sergio@incaser.es>
* Jairo Llopis <yajo.sk8@gmail.com>

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
