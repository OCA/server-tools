otel_web MVP Spec (quick) Goal

Enable browser (Owl) frontend tracing with maximum interoperability by exporting OTLP
over HTTP via a same-origin reverse proxy path to a local OpenTelemetry Collector, while
optionally restricting export to authenticated Odoo users.

Architecture Standard deployment (recommended)

Browser → NGINX (reverse proxy) → Collector (OTLP HTTP receiver) → backends

Browser exports OTLP/HTTP to a same-origin endpoint:

https://<odoo-host>/otlp/v1/traces

NGINX proxies that path to a local Collector (e.g. http://127.0.0.1:4318/v1/traces)

Collector exports to the chosen backend(s)

Important: NGINX’s ngx_otel_module is for NGINX generating/exporting its own spans to
the Collector; it is not an OTLP receiver for browser spans. Collector is the OTLP
receiver.

Data & Protocol Export protocol (frontend)

Use OTLP/HTTP with the standard OTLP paths (/v1/traces)

Prefer same-origin endpoint to avoid CORS complexity and keep cookies flowing naturally.

Propagation (correlation)

Frontend should also attach W3C Trace Context headers (traceparent, optionally
tracestate) to Odoo RPC requests so backend spans become children of frontend spans.

Security & Access Control Options Option 1: Authenticated-only export (recommended
default)

Restrict OTLP ingestion to users with a valid Odoo session.

Mechanism: NGINX auth_request

NGINX uses auth_request to call an internal auth-check endpoint on Odoo.

If Odoo returns 2xx, NGINX proxies the OTLP payload to the Collector.

If Odoo returns 401/403, request is rejected.

auth_request is designed for this subrequest authorization flow. Odoo uses session
cookies (commonly session_id) for authenticated web requests.

Odoo endpoint (in otel_web):

GET /otel/auth_check

Returns:

204 No Content (or 200) if session is authenticated (request.session.uid exists)

401 Unauthorized otherwise

Optional mode: admin-only (check membership in a configured group; return 403 for
non-admin).

Option 2: Allow all users (public website tracing)

No auth_request

Rely on strict NGINX controls (rate limiting, payload size caps, Origin checks)

Recommend conservative client-side sampling.

CSRF / browser abuse mitigation

For OTLP export, prefer standard web mitigations rather than Odoo CSRF tokens (to keep
compatibility with OTel exporters):

Same-origin endpoint (avoid permissive CORS)

Origin/Referer checks at NGINX for /otlp/\*

SameSite cookies (deployment-dependent, but helpful)

Rate limiting + payload caps (mandatory)

(Do not require Odoo CSRF tokens for OTLP export unless you want a custom exporter
flow.)

NGINX requirements (documented, not implemented in Odoo)

Provide a reference config snippet that:

Exposes /otlp/v1/traces publicly

Proxies to local collector OTLP HTTP receiver (127.0.0.1:4318)

Enforces:

limit_req (per IP / per session if feasible)

client_max_body_size

optional Origin/Referer allowlist

optional auth_request → Odoo /otel/auth_check

Collector requirements (documented)

Enable OTLP receiver HTTP (and gRPC if needed for NGINX spans)

Recommend local deployment (same host as Odoo/NGINX) for minimal latency and no extra
third-party hop.

otel_web module deliverables

1. Frontend changes

Patch Owl RPC layer to:

propagate traceparent (and optionally tracestate) on Odoo RPC calls for trace
correlation.

Provide optional JS initializer/config for OTel Web SDK exporter:

OTLP/HTTP endpoint: /otlp/v1/traces

sampling controls (recommended defaults conservative)

2. Backend endpoint (only for auth gating)

Implement /otel/auth_check controller endpoint:

fast, minimal logic

returns only status codes (2xx/401/403)

no payload, no side effects

This endpoint is used exclusively by NGINX auth_request.

3. Documentation

Reference NGINX + Collector configs for:

authenticated-only RUM

public RUM

Clear warnings on:

rate limiting requirements

payload caps

baggage/PII considerations (don’t attach arbitrary baggage to spans by default)

Non-goals for MVP

Odoo acting as an OTLP receiver/forwarder (avoid loading Odoo workers)

Custom “submit spans in RPC payload” approaches (breaks standard OTel export + loses
proper timing)

Mandatory baggage support (keep disabled by default)
