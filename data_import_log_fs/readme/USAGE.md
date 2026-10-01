Create a storage backend (`fs_storage`), then a pick-up under
Data Import > Data Import Settings > Data Import Pick-ups, giving it the
incoming, processing, done and error directories relative to that backend, the
pattern its files are named by, and the format and encoding they arrive in.

The "Data Import: pick files up" scheduled action runs every ten minutes. It
does nothing until a pick-up is active, so a pick-up is what turns a feed on.

Implement `_import_unit`, and if a unit is not a single row, `_group_rows`, on
`data.import.log` — see `data_import_log` for that contract.
