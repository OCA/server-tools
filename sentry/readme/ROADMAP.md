- **No database separation** -- This module functions by intercepting
  all Odoo logging records in a running Odoo process. This means that
  once installed in one database, it will intercept and report errors
  for all Odoo databases, which are used on that Odoo server.
- **Server side only** -- This module reports what the Odoo Python
  process raises. Uncaught JavaScript errors in the web client,
  performance traces, session replays and the [Sentry user feedback
  form](https://docs.sentry.io/product/user-feedback/) are covered by the
  companion
  [`sentry_client`](https://github.com/OCA/server-tools/tree/18.0/sentry_client)
  addon in this repository. The two can share a single Sentry project or
  report into one project each; Sentry recommends one per platform.
