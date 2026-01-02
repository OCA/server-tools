## Introduction

This module upgrades the `base_sparse_field` module to use PostgreSQL's native JSONB
column type instead of TEXT for serialized fields.

**Why JSONB?**

The standard `base_sparse_field` stores serialized attributes as JSON text in a TEXT
column. While functional, this has limitations:

- No database-level indexing on JSON content
- Filtering requires fetching all records and processing in Python
- Less efficient storage (text vs binary)

**What this module provides:**

- **JSONB Storage**: Serialized fields use PostgreSQL JSONB column type
- **GIN Indexes**: Automatic creation of GIN indexes for fast key/value lookups
- **Transparent Upgrade**: Drop-in replacement, no code changes needed
- **Migration Support**: Automatically converts existing TEXT columns to JSONB

**Performance Benefits:**

| Operation           | TEXT (before)            | JSONB (after)      |
| ------------------- | ------------------------ | ------------------ |
| Key existence check | Python loop              | GIN index O(log n) |
| Value filtering     | Full table scan + Python | Index-assisted     |
| Storage size        | ~30% larger              | Binary compressed  |

This module is particularly beneficial when used with `attribute_set` and
`product_attribute_set` for managing dynamic product attributes on e-commerce websites
where filtering performance is critical.

## Configuration

No configuration is required. The module works automatically upon installation.

## Optional: Verify Installation

After installation, you can verify JSONB columns exist:

```sql
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'product_template'
  AND column_name LIKE 'x_custom%';
```

Expected output:

```
      column_name       | data_type
------------------------+-----------
 x_custom_json_attrs    | jsonb
```

## Optional: Verify GIN Index

```sql
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'product_template'
  AND indexname LIKE '%gin%';
```

## Usage

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

If you have existing data in TEXT format, the post-install hook automatically handles
the migration:

```sql
ALTER TABLE product_template
ALTER COLUMN x_custom_json_attrs TYPE jsonb
USING x_custom_json_attrs::jsonb;
```

Empty strings and NULL values are handled gracefully.

## Roadmap

## Planned Enhancements

### ORM Search Integration

Currently, sparse field filtering is done in Python after fetching records. Future
versions may include ORM-level search operators that translate to PostgreSQL JSON
queries:

```python
# Future: Direct ORM filtering on sparse fields
products = env['product.template'].search([
    ('x_capacity', '>', 5000),  # Translated to JSONB query
])
```

### Dynamic Index Creation

Add support for creating targeted indexes on frequently filtered attributes:

```python
# Future: Per-attribute index
attribute.create_search_index()
```

### Search Panel Integration

Native integration with Odoo's search panel widget for attribute filtering on website
product listings.

## Contributors

- OBS Solutions B.V. <https://www.obs-solutions.com>

## Credits

## Development

This module was developed based on discussions and research from:

- [OCA/odoo-pim Issue #153](https://github.com/OCA/odoo-pim/issues/153) - Storage and
  search optimization
- [Akretion Issue #62](https://github.com/akretion/ak-odoo-incubator/issues/62) -
  base_sparse_field evolution
