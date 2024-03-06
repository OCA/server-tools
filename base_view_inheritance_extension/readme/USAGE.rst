**Change a python dictionary (context for example)**


.. code-block:: xml

    <field position="attributes">
        <attribute name="context" operation="update">
            {
                "key": "value",
            }
        </attribute>
    </field>


Note that views are subject to evaluation of xmlids anyways, so if you need
to refer to some xmlid, say ``%(xmlid)s``.

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

**Add domain with AND/OR join operator (AND if missed) for key in attrs**

.. code-block:: xml

    <attribute name="$attribute" operation="attrs_domain_add"
               key="$attrs_key" join_operator="OR">
        $domain_to_add_to_attrs_key
    </attribute>
