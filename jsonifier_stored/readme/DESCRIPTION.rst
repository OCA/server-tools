This module provides a mixin to help storing JSON data.

The idea is that you can pre-compute some data
so that the system does not have to compute it
every time it is asked, for instance, by an external service.

Inspired by the machinery in `connector_search_engine`
(which ideally should be refactored on `jsonifier_stored`)
and by a first experiment for v12 done here
https://github.com/OCA/server-tools/pull/1926.
