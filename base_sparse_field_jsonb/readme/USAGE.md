## Installation

Simply install this module. It will:

1. Patch the `Serialized` field class to use JSONB, including for modules
   importing it directly from `base_sparse_field`
2. Patch `Registry.check_indexes` so Odoo keeps the GIN index of serialized
   fields instead of replacing it by a btree index
3. Migrate the existing TEXT columns of serialized fields to JSONB
4. Create a GIN index on serialized fields defined with `index=True`

Uninstalling the module converts the columns back to TEXT. Restart the server
right afterwards: until then the field class stays patched in the running
process, so updating a module in that window converts the columns to JSONB
again. The round trip is not byte identical: the JSON text is reformatted by
PostgreSQL and a column default dropped during the conversion is not restored.
Both are harmless for `base_sparse_field`, which only parses the JSON.

No configuration is required.

## Compatibility

This module is compatible with:

- `attribute_set` - Dynamic attributes for any model
- `product_attribute_set` - Product-specific attributes
- `website_attribute_set` - E-commerce attribute display and filtering

All modules using `base_sparse_field` automatically benefit from JSONB storage.

## Technical Details

### Column Type Change

Before:
```sql
x_custom_json_attrs TEXT
```

After:
```sql
x_custom_json_attrs JSONB
```

### GIN Index

No index is created by default. Set `index=True` on the serialized field to
get a GIN index, which supports the `?`, `?|`, `?&` and `@>` operators. Other
index values (`"btree"`, `"btree_not_null"`, `"trigram"`) are not supported:
a warning is logged and a plain GIN index is created instead.

```python
x_custom_json_attrs = fields.Serialized(index=True)
```

```sql
CREATE INDEX product_template__x_custom_json_attrs_index
ON product_template USING GIN (x_custom_json_attrs);
```

### Querying JSONB (Advanced)

With JSONB, you can use PostgreSQL's native JSON operators in raw SQL:

```sql
-- Find products where x_capacity > 5000
SELECT * FROM product_template
WHERE x_custom_json_attrs->>'x_capacity' > '5000';

-- Find products with a specific attribute
SELECT * FROM product_template
WHERE x_custom_json_attrs ? 'x_fire_suppression_system';

-- Find products matching multiple criteria
SELECT * FROM product_template
WHERE x_custom_json_attrs @> '{"x_power_type": "electric"}';
```

## Migration from TEXT

If you have existing data in TEXT format, the post-install hook automatically
handles the migration:

```sql
ALTER TABLE product_template
ALTER COLUMN x_custom_json_attrs TYPE jsonb
USING x_custom_json_attrs::jsonb;
```

Empty strings and NULL values are handled gracefully. Indexes on the converted
column are dropped first, as indexes built for TEXT can not be rebuilt on JSONB.
Indexes on other columns are left untouched.

**Plan the installation on large tables.** Changing the column type rewrites
the whole table under an `ACCESS EXCLUSIVE` lock, and every converted table
stays locked until the end of the installation transaction. Creating the GIN
index takes a lock as well. On big `attribute_set` or `queue_job` tables, run
the installation in a maintenance window. A single row holding text that is
not valid JSON aborts the installation; check the data beforehand, e.g.:

```sql
SELECT id FROM queue_job
WHERE dependencies IS NOT NULL AND dependencies <> ''
  AND NOT pg_input_is_valid(dependencies, 'jsonb');  -- PostgreSQL 16+
```
