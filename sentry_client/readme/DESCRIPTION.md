Capture uncaught JS errors and unhandled promise rejections in the Odoo web
client to Sentry, with optional Performance Monitoring (BrowserTracing),
Session Replay, Browser CPU Profiling, and Console-log capture tiers
behind explicit opt-in toggles.

The Sentry browser SDK ships **vendored inside the module** — no external
CDN call, air-gapped friendly out of the box.

**Standalone:** works on its own. Reads DSN / release / environment from
the `sentry_*` options in `odoo.conf`. Captures browser-side errors only.

**Better together with `sentry`:** install alongside the server-side
[`sentry`](../sentry) module to cluster client and server errors for the
same user / release / environment into one Sentry issue. Both modules
share the same `sentry_*` config options by convention — fill them in
once and client + server events land in the same Sentry project.

Each tier above Tier 0 is **off by default** and surfaces an in-form
warning about its perf cost when enabled. Sample rates are sliders so
admins can dial behaviour without a server restart. Individual users can
opt out of session replay via their own preferences page.
