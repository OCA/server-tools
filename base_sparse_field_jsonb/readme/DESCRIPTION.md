This module upgrades the `base_sparse_field` module to use PostgreSQL's native
JSONB column type instead of TEXT for serialized fields.

**Why JSONB?**

The standard `base_sparse_field` stores serialized attributes as JSON text in a
TEXT column. While functional, this has limitations:

- No database-level indexing on JSON content
- Filtering requires fetching all records and processing in Python
- The JSON is parsed again on every read

**What this module provides:**

- **JSONB Storage**: Serialized fields use PostgreSQL JSONB column type
- **GIN Indexes**: Serialized fields defined with `index=True` get a GIN index
  for fast key/value lookups
- **Transparent Upgrade**: Drop-in replacement, no code changes needed
- **Migration Support**: Converts existing TEXT columns to JSONB, also for
  modules installed later on, and back to TEXT when uninstalled

**What changes:**

| Operation | TEXT (before) | JSONB (after) |
|-----------|---------------|---------------|
| Key existence check | Python loop | `?` operator, GIN index when `index=True` |
| Value filtering | Full table scan + Python | `@>` / `->>` operators in SQL |
| Storage | JSON text | Binary JSONB |

This module is particularly beneficial when used with `attribute_set` and
`product_attribute_set` for managing dynamic product attributes on e-commerce
websites where filtering performance is critical.
