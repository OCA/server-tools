## Automatic Activation

This module auto-installs when `base_sparse_field_jsonb` is installed.
No additional configuration is required.

## How It Works

When you search on a model with sparse fields:

```python
# Standard Odoo search on a sparse field
products = self.env['product.template'].search([
    ('x_color', '=', 'red'),
    ('x_manufacturing_year', 'in', ['2022', '2023', '2024']),
])
```

The module automatically:

1. Detects that `x_color` and `x_manufacturing_year` are sparse fields
2. Identifies their container field (e.g., `x_custom_json`)
3. Translates the domain to JSONB operators
4. Executes the query using PostgreSQL's GIN index

## Debugging

Enable debug logging to see the JSONB translations:

```python
import logging
logging.getLogger('odoo.addons.base_sparse_field_jsonb_search').setLevel(logging.DEBUG)
```

This will log messages like:

```
JSONB search: product_template.x_color = 'red' -> x_custom_json->>'x_color'
```

## Limitations

- Sorting on sparse fields is not supported (would require additional indexes)
- Complex nested JSON paths are not supported
- Full-text search requires additional configuration
