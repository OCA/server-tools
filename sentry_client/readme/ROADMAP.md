* **Server-side distributed-trace propagation** — `release` and
  `environment` are shared with the OCA `sentry` server-side module by
  convention (same `sentry_*` options), and the browser already sends
  the right user context. Full distributed tracing (server span ⇄
  browser span correlation) would need OpenTelemetry hooks in the
  server-side `sentry` module too — out of scope for this module; will
  go in a follow-up PR against `sentry/`.
* **OWL error-boundary depth** — the current handler captures the
  failing component tree + props. Could also enrich with the action
  context (active model, record IDs, view type) by reading
  `env.services.action.currentController`. Optional polish.
* **Asset-bundle profiling preload** — the JS Self-Profiling API needs
  the `Document-Policy: js-profiling` HTTP header on the document
  response, which Odoo doesn't emit by default. CONFIGURE.md documents
  the nginx workaround; a small `ir.http.dispatch` hook in this module
  could set the header conditionally when Tier 3 profiling is on.
