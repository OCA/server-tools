Database Autovacuum Tuning helps administrators keep PostgreSQL healthy by
exposing recommended autovacuum settings in Odoo. It provides guidance and
documentation for sizing thresholds and scale factors so large, busy databases
avoid table bloat and excessive vacuum lag. Use it to standardize autovacuum
configuration across environments and speed up maintenance operations without
manual tuning.

This module is mostly useful for PostgreSQL <= 17. PostgreSQL 18.0 introduces
the `autovacuum_vacuum_max_threshold` parameter, which already provides the
capability this module targets.

The `pgstattuple` extension must be installed on the database.