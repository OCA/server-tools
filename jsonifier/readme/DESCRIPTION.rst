This module adds a 'jsonify' method to every model of the ORM.
It works on the current recordset and requires a single argument 'parser'
that specify the field to extract.

Example of a simple parser:


.. code-block:: python

    parser = [
        'name',
        'number',
        'create_date',
        ('partner_id', ['id', 'display_name', 'ref'])
        ('line_id', ['id', ('product_id', ['name']), 'price_unit'])
    ]

In order to be consistent with the Odoo API the jsonify method always
returns a list of objects even if there is only one element in the recordset.

By default the key into the JSON is the name of the field extracted
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
that generate a parser from an ir.exports configuration.

Further features are available for advanced uses.
It defines a simple "resolver" model that has a "python_code" field and a resolve
function so that arbitrary functions can be configured to transform fields,
or process the resulting dictionary.
It is also to specify a lang to extract the translation of any given field.

To use these features, a full parser follows the following structure:

.. code-block:: python

    parser = {
        "resolver": 3,
        "language_agnostic": True,
        "langs": {
            False: [
                {'name': 'description'},
                {'name': 'number', 'resolver': 5},
                ({'name': 'partner_id', 'target': 'partner'}, [{'name': 'display_name'}])
            ],
            'fr_FR': [
                {'name': 'description', 'target': 'descriptions_fr'},
                ({'name': 'partner_id', 'target': 'partner'}, [{'name': 'description', 'target': 'description_fr'}])
            ],
        }
    }


One would get a result having this structure (note that the translated fields are merged in the same dictionary):

.. code-block:: python

    exported_json == {
        "description": "English description",
        "description_fr": "French description, voilà",
        "number": 42,
        "partner": {
            "display_name": "partner name",
            "description_fr": "French description of that partner",
        },
    }


Note that a resolver can be passed either as a recordset or as an id, so as to be fully serializable.
A slightly simpler version in case the translation of fields is not needed,
but other features like custom resolvers are:

.. code-block:: python

    parser = {
        "resolver": 3,
        "fields": [
                {'name': 'description'},
                {'name': 'number', 'resolver': 5},
                ({'name': 'partner_id', 'target': 'partners'}, [{'name': 'display_name'}]),
        ],
    }


By passing the `fields` key instead of `langs`, we have essentially the same behaviour as simple parsers,
with the added benefit of being able to use resolvers.

Standard use-cases of resolvers are:
- give field-specific defaults (e.g. `""` instead of `None`)
- cast a field type (e.g. `int()`)
- alias a particular field for a specific export
- ...

A simple parser is simply translated into a full parser at export.

If the global resolver is given, then the json_dict goes through:

.. code-block:: python

    resolver.resolve(dict, record)

Which allows to add external data from the context or transform the dictionary
if necessary. Similarly if given for a field the resolver evaluates the result.

It is possible for a target to have a marshaller by ending the target with '=list':
in that case the result is put into a list.

.. code-block:: python

  parser = {
      fields: [
          {'name': 'name'},
          {'name': 'field_1', 'target': 'customTags=list'},
          {'name': 'field_2', 'target': 'customTags=list'},
      ]
  }


Would result in the following JSON structure:

.. code-block:: python

    {
        'name': 'record_name',
        'customTags': ['field_1_value', 'field_2_value'],
    }

The intended use-case is to be compatible with APIs that require all translated
parameters to be exported simultaneously, and ask for custom properties to be
put in a sub-dictionary.
Since it is often the case that some of these requirements are optional,
new requirements could be met without needing to add field or change any code.

Note that the export values with the simple parser depends on the record's lang;
this is in contrast with full parsers which are designed to be language agnostic.


NOTE: this module was named `base_jsonify` till version 14.0.1.5.0.
