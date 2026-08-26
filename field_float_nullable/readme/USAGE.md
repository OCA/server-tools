This module is intended for developers who need to preserve the distinction between NULL and 0.0 in float fields.
Unlike standard fields.Float, this field stores None (which becomes NULL in PostgreSQL) when left empty, rather than converting to 0.0.

The float_nullable field type allows developers to create float fields in Odoo that remain empty (NULL) in the database unless explicitly filled.

## Field declaration

To declare a field of type float_nullable, use the FloatNullable class:

```python

from odoo import models, fields


class YourModel(models.Model):
    _name = 'your.model'

    nullable_price = fields.FloatNullable(
        string="Special Float",
        digits=(4,4),
        help="Number NULL if not set"
    )
```

Stores None (not 0.0) when empty

Integrates with form, tree, and export views

Fully filterable with custom filters (search bar)

Can be used anywhere a regular float field would be used

This field accepts the same options as Odoo's standard fields.Float, such as:

    `digits`: to control decimal precision