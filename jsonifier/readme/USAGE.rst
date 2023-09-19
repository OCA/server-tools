with_fieldname parameter
==========================

The with_fieldname option of jjsonify() method, hen true,  will inject on
the same level of the data fieldname_$field keys that will
give us the field name , in current user language of the field itself.
This will add keys for translated front-end labels, without disrupting the access
to existing code.


   Examples of with_fieldname usage:

.. code-block:: python

    # example 1
    parser = [('name')]
    a.jsonify(parser=parser)
    [{'name': 'SO3996'}]
    >>> a.jsonify(parser=parser, with_fieldname=False)
    [{'name': 'SO3996'}]
    >>> a.jsonify(parser=parser, with_fieldname=True)
    [{'fieldname_name': 'Order Reference', 'name': 'SO3996'}}]


    # example 2 - with a subparser-
    parser=['name', 'create_date', ('order_line', ['id' , 'product_uom', 'is_expense'])]
    >>> a.jsonify(parser=parser, with_fieldname=False)
    [{'name': 'SO3996', 'create_date': '2015-06-02T12:18:26.279909+00:00', 'order_line': [{'id': 16649, 'product_uom': 'stuks', 'is_expense': False}, {'id': 16651, 'product_uom': 'stuks', 'is_expense': False}, {'id': 16650, 'product_uom': 'stuks', 'is_expense': False}]}]
    >>> a.jsonify(parser=parser, with_fieldname=True)
    [{'fieldname_name': 'Order Reference', 'name': 'SO3996', 'fieldname_create_date': 'Creation Date', 'create_date': '2015-06-02T12:18:26.279909+00:00', 'fieldname_order_line': 'Order Lines', 'order_line': [{'fieldname_id': 'ID', 'id': 16649, 'fieldname_product_uom': 'Unit of Measure', 'product_uom': 'stuks', 'fieldname_is_expense': 'Is expense', 'is_expense': False}]}]
