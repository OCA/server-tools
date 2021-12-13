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
