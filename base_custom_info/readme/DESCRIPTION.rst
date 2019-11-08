This module allows you to attach custom information to records without the need
to alter the database structure too much.

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
