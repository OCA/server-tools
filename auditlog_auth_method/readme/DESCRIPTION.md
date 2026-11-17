This module extends **auditlog** to record on every log how the user
authenticated: web session (password, OAuth, superuser mode), XML-RPC or
JSON-RPC (password, API key, OAuth token), token route, public access or
server-side code. Each rule can be limited to some of these methods, for
example to audit only the operations done with an API key. RPC calls, which
**auditlog** logs without an HTTP request, get one that keeps their path,
client IP and user agent.
