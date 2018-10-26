**Change a python dictionary (context for example)**


.. code-block:: xml

    <attribute name="$attribute" operation="python_dict" key="$key">
        $new_value
    </attribute>

Note that views are subject to evaluation of xmlids anyways, so if you need
to refer to some xmlid, say ``%(xmlid)s``.

**Move an element in the view**

.. code-block:: xml

    <xpath expr="$xpath" position="move" target="$targetxpath" />

This can also be used to wrap some element into another, create the target
element first, then move the node youwant to wrap there.

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
