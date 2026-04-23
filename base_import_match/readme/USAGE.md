Prepare your CSV or XLSX file using only business columns — no External ID column
required.

**Example** — update e-commerce category descriptions matching by name **and** seo_name:

```text
name,seo_name,description
Smartphones,Electronics,All our smartphone models
Laptops,Electronics,Premium laptop range
```

When importing into `product.public.category`:

- **Unique match** (`name` + `seo_name` → one record found): the existing record is
  updated.
- **No match**: a new record is created.
- **Multiple matches**: the row is skipped and a warning is written to the server log to
  avoid ambiguous writes.

> **Note:** If your file already contains an `id` or `.id` column, this module
> deactivates itself for that import and Odoo's standard behaviour applies.

### Many2one resolution

For many2one fields (e.g. `website_id`), the raw string value from the import file is
resolved to a database ID via an exact `name_search`. If zero or more than one related
record matches the display name, the row is treated as a new record (no update is
performed) and a message is written to the log.
