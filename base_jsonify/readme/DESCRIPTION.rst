This module adds a 'jsonify' method to every model of the ORM.
It works on the current recordset and requires a single argument 'parser'
that specify the field to extract.

Example of parser:


.. code-block:: python

    parser = [
        'name',
        'number',
        'create_date',
        ('partner_id', ['id', 'display_name', 'ref'])
        ('line_id', ['id', ('product_id', ['name']), 'price_unit'])
    ]

In order to be consitent with the odoo api the jsonify method always
return a list of object even if there is only one element in input

By default the key into the json is the name of the field extracted
from the model. If you need to specify an alternate name to use as key, you
can define your mapping as follow into the parser definition:

.. code-block:: python

    parser = [
         'field_name:json_key'
    ]

.. code-block:: python


    parser = [
        'name',
        'number',
        'create_date:creationDate',
        ('partner_id:partners', ['id', 'display_name', 'ref'])
        ('line_id:lines', ['id', ('product_id', ['name']), 'price_unit'])
    ]

If you need to parse the value of a field in a custom way,
you can pass a callable or the name of a method on the model:

.. code-block:: python

    parser = [
        ('name', "jsonify_name")  # method name
        ('number', lambda rec, field_name: rec[field_name] * 2))  # callable
    ]

Also the module provide a method "get_json_parser" on the ir.exports object
that generate a parser from an ir.exports configuration
