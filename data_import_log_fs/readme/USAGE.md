Create a storage backend (`fs_storage`), then a pick-up under
Data Import > Data Import Settings > Data Import Pick-ups, giving it the
incoming, processing, done and error directories relative to that backend, the
pattern its files are named by, and the format and encoding they arrive in.

Leave the processing directory empty when the storage offers none: a file then
stays in the incoming directory while it is imported, and its open import log
keeps a later scan from taking it again. A file replaced there during its
import is left for the next scan rather than filed as done.

The "Data Import: pick files up" scheduled action runs every ten minutes. It
does nothing until a pick-up is active, so a pick-up is what turns a feed on.

A pick-up whose storage cannot be reached is skipped, and the others are still
scanned. Its files wait where they are and are taken in by the first scan that
succeeds. The first failure is posted on the pick-up for the users of the "Job
Queue Manager" group, who are made its followers; the failures after it only
update the error shown on the pick-up, until a scan succeeds and clears it.

Implement `_import_unit`, and if a unit is not a single row, `_group_rows`, on
`data.import.log` — see `data_import_log` for that contract.
