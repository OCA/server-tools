## Installation

Simply install this module. It will:

1. Override the `Serialized` field class to use JSONB
2. Migrate any existing TEXT columns to JSONB
3. Create GIN indexes on all serialized field columns

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

The module creates GIN indexes for fast lookups:

```sql
CREATE INDEX idx_product_template_x_custom_json_attrs_gin
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

Empty strings and NULL values are handled gracefully.
