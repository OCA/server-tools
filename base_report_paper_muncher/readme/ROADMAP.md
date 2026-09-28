- Paper Muncher is only supported on Linux and macOS (not Windows).
- WebSocket requests are rejected by the HTTP-over-pipe server.
- Rendering timeout: 15 minutes (`SERVE_TIMEOUT`).
- Pipe write timeout: 15 seconds (`WRITE_TIMEOUT`).
- The binary must be installed on the system; this module only integrates the
  communication layer.
