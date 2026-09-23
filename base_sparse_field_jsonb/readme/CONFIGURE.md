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
