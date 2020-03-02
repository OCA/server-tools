**Change a python dictionary (context for example)**


.. code-block:: xml

    <attribute name="$attribute" operation="python_dict" key="$key">
        $new_value
    </attribute>

Note that views are subject to evaluation of xmlids anyways, so if you need
to refer to some xmlid, say ``%(xmlid)s``.

**Move an element in the view**

This feature is now native, cf the `official Odoo documentation <https://www.odoo.com/documentation/12.0/reference/views.html#inheritance-specs>`_.

**Add/remove values in a list (states for example)**

This feature is now native but not documented in the official Odoo documentation. You can have a look at the `Odoo soure code <https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/models/ir_ui_view.py#L668>`_ and look for `this example <https://github.com/odoo/odoo/blob/12.0/addons/website_mass_mailing/views/snippets_templates.xml#L55>`_ in the website_mass_mailing module.
