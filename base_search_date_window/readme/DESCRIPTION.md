This module adds `search.date.window.mixin`, an abstract model that limits
every search on the models that inherit it to a date window around the
current date, unless the search already bounds that date itself.

It is meant for models with very large tables (GPS positions, IoT readings,
logs...) where a search without a date condition reads far too many rows, or
scans every partition of a table partitioned by date.

**Warning:** inheriting the mixin changes what `search()` returns by default.
A search with no date condition no longer returns old records (or records
too far in the future). Code that has to find a record regardless of its date
must disable the window explicitly (see *Usage*).
