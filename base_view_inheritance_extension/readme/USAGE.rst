**Change a python dictionary (context for example)**


.. code-block:: xml

    <attribute name="$attribute" operation="python_dict" key="$key">
        $new_value
    </attribute>

Note that views are subject to evaluation of xmlids anyways, so if you need
to refer to some xmlid, say ``%(xmlid)s``.

**Add to values in a list (states for example)**

.. code-block:: xml

    <attribute name="$attribute" operation="list_add">
        $new_value(s)
    </attribute>

**Remove values from a list (states for example)**

.. code-block:: xml

    <attribute name="$attribute" operation="list_remove">
        $remove_value(s)
    </attribute>

**Add text after and/or before than original**

.. code-block:: xml

    <attribute name="$attribute" operation="text_add">
        $text_before {old_value} $text_after
    </attribute>

**Add domain with AND/OR join operator (AND if missed) allowing conditional changes**

.. code-block:: xml

    <attribute name="$attribute" operation="domain_add"
               condition="$field_condition" join_operator="OR">
        $domain_to_add
    </attribute>

**Move an element in the view**

This feature is now native, cf the `official Odoo documentation <https://www.odoo.com/documentation/12.0/reference/views.html#inheritance-specs>`_.
