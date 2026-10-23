This module enables native PostgreSQL JSONB search operators for sparse fields
stored in Serialized containers.

When combined with `base_sparse_field_jsonb`, which upgrades Serialized fields
from TEXT to JSONB storage, this module translates Odoo search domains into
native PostgreSQL JSONB operators for significantly improved query performance.

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

| Odoo Operator | JSONB Translation |
|---------------|-------------------|
| `=` | `jsonb->>'key' = 'value'` |
| `!=` | `jsonb->>'key' != 'value'` |
| `in` | `jsonb->>'key' IN (...)` |
| `not in` | `jsonb->>'key' NOT IN (...)` |
| `like` | `jsonb->>'key' LIKE '%value%'` |
| `ilike` | `jsonb->>'key' ILIKE '%value%'` |
| `>`, `>=`, `<`, `<=` | Numeric cast + comparison |

## Boolean Fields

Boolean sparse fields are handled specially:

```sql
-- Check if boolean field is True
WHERE (jsonb->'field')::boolean = TRUE

-- Check if boolean field is False or not set
WHERE (jsonb->'field' IS NULL OR (jsonb->'field')::boolean = FALSE)
```
