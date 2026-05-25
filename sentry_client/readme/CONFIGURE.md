## 1. Pick where the DSN comes from

There are two ways to point the browser SDK at a Sentry project. Use **one**:

**(a) Recommended — separate browser DSN via the Settings UI.** Sentry's own
guidance is one project per platform: a Python project for backend errors
and a JavaScript-Browser project for client-side errors. Set the dedicated
browser DSN under **Settings → General Settings → Sentry Browser Monitoring
→ Connection**:

| Field | Example | Notes |
|---|---|---|
| **Browser DSN** | `https://<public_key>@sentry.example.com/<project_id>` | Public DSN of the JavaScript project. Safe to embed in client code per Sentry's docs. |
| **Environment** | `production-web` | Tags every browser event. May differ from the backend env tag. |
| **Release** | asset-bundle hash or deploy SHA | Tags every browser event. May differ from the Odoo Python release. |

No Odoo restart required — changes take effect on the next page load.

**(b) Fallback — shared DSN via `odoo.conf`.** If the Connection fields
above are left blank, the controller reads the same top-level `sentry_*`
options the OCA server-side `sentry` module uses on the 18.0 series (the
dedicated `[sentry]` section only exists from 19.0):

```ini
[options]
sentry_dsn = https://<public_key>@sentry.example.com/<project_id>
sentry_release = 1.3.2
sentry_environment = production
```

This path is convenient for single-project deployments that want both
backend Python events and browser JavaScript events going to the same
Sentry project. Editing `odoo.conf` requires an Odoo restart.

The UI value always wins when both are set.

## 2. Settings → General Settings → Sentry Browser Monitoring

Each tier is independently toggleable:

### Tier 0 — Capture browser errors (recommended default once a DSN is set)

Loads `bundle.min.js` (~30KB gzipped). Wires `window.onerror` and
`window.onunhandledrejection`. Sends events with the logged-in user's id +
email as `Sentry.setUser(...)`.

### Tier 1 — Performance monitoring

Enables `BrowserTracing`. Auto-instruments fetch / XHR, navigation timing,
and long-task observer. **Adds roughly 5–10% per-request overhead at sample
rate 1.0** plus extra bandwidth per traced request. Recommended in
production: `0.05` or below.

### Tier 2 — Session replay

Enables `@sentry/replay`. **Adds ~100KB to every page** and records DOM
mutations + console + network activity. Strongly recommend
`Healthy-session sample = 0.0` and `On-error sample = 1.0` so recording
only kicks in for sessions that already hit an error.

### Tier 3 — Optional extras

* **User feedback widget** — adds a feedback button.
* **Browser CPU profiling** — captures JS Self-Profiling samples for
  traced transactions. Has its own sample-rate slider. **Requires the
  page to be served with a `Document-Policy: js-profiling` HTTP header.**
  See "Browser profiling — extra setup" below.
* **Console-log capture** — uploads `console.log` / `console.warn` calls
  as Sentry Log entries. Spammy without filtering.

## 3. User preferences → Privacy — per-user session-replay opt-out

Each user can disable session replay for their own sessions, regardless of
the database-wide Tier 2 setting. The browser SDK still loads (the bundle
URL doesn't change), but the Replay integration is never registered for
the opted-out user — no DOM observer, no recording.

To enable: open the user's profile (top-right avatar → My Profile →
Preferences → Privacy) and check **Disable Sentry session replay**.

The toggle is self-writeable: users can manage it without administrator
help.

What leaves the server per user: events carry the numeric user id plus the
user's `res.groups` names and categories as the `odoo.groups` /
`odoo.category` tags (for triage filtering — e.g. admin vs portal). No
email or display name is sent; replay masking covers all text, inputs and
media by default. If group names are sensitive in your deployment, keep in
mind they are delivered to whatever Sentry instance the DSN points at.

## 4. OWL component context on backend errors

When the OCA `sentry_client` module is installed and Tier 0 is on, any
OWL-component-raised exception in the backend (`/odoo/*`) is captured to
Sentry with two extra fields:

- `tags.owl = true`
- `extra.component_tree` — the OWL component path of the failing render

This complements (not replaces) Odoo's standard *"Oops!"* dialog — both
fire side by side. No configuration needed; the handler registers
automatically when the module is installed.

## Browser profiling — extra setup

The JS Self-Profiling API requires the browser to receive a permission
header on the document HTML response:

```
Document-Policy: js-profiling
```

Odoo's default web responses do not emit this header. You'll need to add
it at your reverse proxy. nginx example:

```nginx
location /odoo {
    proxy_pass http://odoo:8069;
    add_header Document-Policy "js-profiling";
}
```

Without the header, the Profiling integration registers cleanly and
sends profile payloads, but they will be empty — no client-side error,
just no useful data in Sentry's Profiling tab.

## Vendored Sentry SDK

The browser SDK ships **vendored inside the module** under
`sentry_client/static/lib/sentry/<version>/`. The default
**Sentry SDK source URL** points at this in-module path, so the browser
loads the SDK from the same origin as Odoo — no traffic to
`browser.sentry-cdn.com`, no air-gap workarounds needed.

To bump the vendored version, run the refresh script:

```bash
cd sentry_client/
./scripts/refresh-vendor-bundle.sh 10.55.0   # whatever you want
git add static/lib/sentry/10.55.0/
git commit -m "[IMP] sentry_client: bump vendored SDK to 10.55.0"
```

The script downloads each bundle from `browser.sentry-cdn.com`, verifies
it against Sentry's published SHA-384 SRI hash, drops the LICENSE file,
and writes a SHA256SUMS for reviewers. After committing, update the
**Sentry SDK version** in Settings → General Settings → Sentry Browser
Monitoring to match.

To revert to the public CDN at runtime (e.g. for quick A/B testing),
override **Sentry SDK source URL** to
`https://browser.sentry-cdn.com` in the Settings page.

## Sentry server compatibility

The browser SDK talks to whatever Sentry instance you point the DSN at —
either sentry.io or a self-hosted instance. Feature support depends on
the Sentry server version:

| Feature | Minimum Sentry server | Notes |
|---|---|---|
| Tier 0 — error capture | v9.0+ | Basic event ingest, supported by every modern Sentry. |
| Tier 1 — performance / tracing | v10.0+ | The tracing UI shipped in Sentry 10. |
| Tier 2 — session replay | v22.10.0+ (Oct 2022) + feature flag | Replay ingest was introduced in self-hosted 22.10. The feature must also be enabled on the server: set `SENTRY_FEATURES["organizations:session-replay"] = True` (and `…-ui`, `…-recording-scrubbing`) in `sentry.conf.py`, then restart `web` + `ingest-replay-recordings`. Without the flag, browser envelopes arrive at `/api/<n>/envelope/` but are silently discarded — no UI surface, no error. |
| Tier 3 — feedback widget | v23.6.0+ (Jun 2023) | The modern programmatic feedback API. Older versions still work with the legacy `Sentry.showReportDialog` path, which this module does not use. |
| Tier 3 — browser profiling | v24.0+ (Jan 2024) | Plus the `Document-Policy: js-profiling` header (see above). |
| Tier 3 — console-log capture | v25.0+ (Mar 2025) | Sentry Logs API. Server versions before v25 will ingest the events as a generic log envelope; the dedicated Logs UI requires v25+. |

For sentry.io: all features are always available.

For self-hosted: check your tag at `/opt/sentry/install/_version.sh` (or
`docker exec <sentry-web> sentry --version`). If a feature you've enabled
isn't supported by your Sentry server, the browser SDK still sends the
envelope but the server discards it — no client-side error.
