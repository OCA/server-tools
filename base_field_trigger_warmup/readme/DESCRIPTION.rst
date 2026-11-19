The ORM resolves the transitive closure of compute triggers lazily: the first
time a field is written, Odoo walks its ``@api.depends`` graph and caches the
resulting trigger tree in the registry. On models with many interdependent
stored computed fields, that first write pays for the whole closure, so the
first request served by each worker is noticeably slower than the ones that
follow, and every restart brings the penalty back.

This module builds those trees while the registry loads, where no user is
waiting. It has no user interface and no effect on behaviour: it only decides
*when* work the ORM would do anyway is done.

It was extracted from a production deployment whose invoice line model carries
around 180 interdependent stored fields: the first write on a fresh worker cost
about five times what every following write cost. Warming up the trees at boot
removed the difference.
