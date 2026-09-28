## Introduction

This module enables native PostgreSQL JSONB search operators for sparse fields stored in
Serialized containers.

When combined with `base_sparse_field_jsonb`, which upgrades Serialized fields from TEXT
to JSONB storage, this module translates Odoo search domains into native PostgreSQL
JSONB operators for significantly improved query performance.

## Performance Improvement

Without this module, searching on sparse fields requires:

1. Loading all records from the database
2. Deserializing JSON data in Python
3. Filtering records in Python memory

With this module, the same search uses native PostgreSQL:

```sql
-- Native JSONB query (fast, uses GIN index)
SELECT * FROM product_template
WHERE x_custom_json->>'x_color' = 'red'
```

## Supported Operators

| Odoo Operator        | JSONB Translation               |
| -------------------- | ------------------------------- |
| `=`                  | `jsonb->>'key' = 'value'`       |
| `!=`                 | `jsonb->>'key' != 'value'`      |
| `in`                 | `jsonb->>'key' IN (...)`        |
| `not in`             | `jsonb->>'key' NOT IN (...)`    |
| `like`               | `jsonb->>'key' LIKE '%value%'`  |
| `ilike`              | `jsonb->>'key' ILIKE '%value%'` |
| `>`, `>=`, `<`, `<=` | Numeric cast + comparison       |

## Boolean Fields

Boolean sparse fields are handled specially:

```sql
-- Check if boolean field is True
WHERE (jsonb->'field')::boolean = TRUE

-- Check if boolean field is False or not set
WHERE (jsonb->'field' IS NULL OR (jsonb->'field')::boolean = FALSE)
```

## Usage

## Automatic Activation

This module auto-installs when `base_sparse_field_jsonb` is installed. No additional
configuration is required.

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

## Contributors

- OBS Solutions B.V. <https://www.obs-solutions.com>
- Stefcy <hello@stefcy.com>

## Credits

## Development

This module was developed by OBS Solutions B.V.
