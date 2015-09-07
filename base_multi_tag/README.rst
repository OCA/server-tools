.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
Base Multi Tag
==============

This module was written to provide generic way to add tags to any Odoo model.
This module contains basic models and views for tags.
Adding tags to models should be implemented by separate modules.


Usage
=====

To add tags to your model just folow few simple steps below:

1. Add ``base_multi_tag`` module as dependency for your module

2. Use inherit from ``"res.tag.mixin"`` to get tags functionality to your model, like::

    class Product(orm.Model):
        _name = "product.product"
        _inherit = ["product.product",
                    "res.tag.mixin"]

3. Add record to taggable models registry::
   
    <record model="res.tag.model" id="res_tag_model_product_product">
      <field name="name">Product</field>
      <field name="model">product.product</field>
    </record>

4. Now You can use ``tag_ids`` field in Your views for Your model:

   - search view::
    
        <field name="tag_ids" string="Tag"
            filter_domain="['|',('tag_ids.name','ilike',self),('tag_ids.code','ilike',self)]"/>
        <field name="no_tag_id" string="No tag"/>  <!-- For invers searching (items that do not contain tag)-->

   - tree view::
  
        <field name="tag_ids" widget="many2many_tags" placeholder="Tags..."/>

   - form view::
    
        <field name="tag_ids"
            widget="many2many_tags"
            placeholder="Tags..."
            context="{'default_model': 'product.product'}"/>
    
    Pay attention on context field. This will allow to avoid tag form popup when adding tag from form field


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/{project_repo}/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/server-tools/issues/new?body=module:%20base_multi_tag%0Aversion:%20{version}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

Contributors
------------

* Dmytro Katyukha <firemage.dime@gmail.com>


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
