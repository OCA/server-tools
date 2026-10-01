This module upgrades the `base_sparse_field` module to use PostgreSQL's native
JSONB column type instead of TEXT for serialized fields.

**Why JSONB?**

The standard `base_sparse_field` stores serialized attributes as JSON text in a
TEXT column. While functional, this has limitations:

- No database-level indexing on JSON content
- Filtering requires fetching all records and processing in Python
- Less efficient storage (text vs binary)

**What this module provides:**

- **JSONB Storage**: Serialized fields use PostgreSQL JSONB column type
- **GIN Indexes**: Automatic creation of GIN indexes for fast key/value lookups
- **Transparent Upgrade**: Drop-in replacement, no code changes needed
- **Migration Support**: Automatically converts existing TEXT columns to JSONB

**Performance Benefits:**

| Operation | TEXT (before) | JSONB (after) |
|-----------|---------------|---------------|
| Key existence check | Python loop | GIN index O(log n) |
| Value filtering | Full table scan + Python | Index-assisted |
| Storage size | ~30% larger | Binary compressed |

This module is particularly beneficial when used with `attribute_set` and
`product_attribute_set` for managing dynamic product attributes on e-commerce
websites where filtering performance is critical.
