**Change a python dictionary (context for example)**


.. code-block:: xml

    <attribute name="$attribute" operation="python_dict" key="$key">
        $new_value
    </attribute>

Note that views are subject to evaluation of xmlids anyways, so if you need
to refer to some xmlid, say ``%(xmlid)s``.

**Add to values in a list (states for example)**

Deprecated. This feature is now native, use `<attribute name="attrname" separator="," add="something" />`.

**Remove values from a list (states for example)**

Deprecated. This feature is now native, use `<attribute name="attrname" separator="," remove="something" />`.

**Move an element in the view**

This feature is now native, cf the `official Odoo documentation <https://www.odoo.com/documentation/14.0/developer/reference/addons/views.html#inheritance-specs>`_.
