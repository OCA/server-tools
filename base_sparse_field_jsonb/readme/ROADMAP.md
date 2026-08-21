## Planned Enhancements

### ORM Search Integration

Currently, sparse field filtering is done in Python after fetching records.
Future versions may include ORM-level search operators that translate to
PostgreSQL JSON queries:

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

Native integration with Odoo's search panel widget for attribute filtering
on website product listings.
