Universal JSON / Schema Export Engine for Odoo.

This module provides a complete framework for exporting data from any Odoo model
as structured JSON, with support for:

- **Dynamic Schema Builder**: Use Odoo's built-in export field selector to
  interactively choose which fields (including nested relational fields) to
  include in your JSON output. No code required.

- **JSON Schema Generation**: Auto-generates a JSON Schema (draft-07) from the
  selected fields and model definition, including field types, nullable markers,
  selection enums, and nested relational structures. Available both in the UI
  and via a dedicated REST endpoint.

- **REST API Endpoints**: Generate REST-like API endpoints for any schema with
  configurable authentication (none, API key, or session-based), pagination,
  and CORS support. Each endpoint exposes both a data URL and a schema URL.

- **Webhooks**: Push data to external systems automatically when records are
  created, updated, or deleted. Supports HMAC-SHA256 signing, custom headers,
  and retry with exponential backoff.

- **Scheduled Exports**: Export data on a schedule (minutes, hours, days, weeks)
  as JSON or JSON Lines files, delivered as Odoo attachments or HTTP POST to
  an external URL. Supports incremental exports (only changed records).

- **Export Logs**: Full audit trail of all export operations (API calls, webhooks,
  scheduled exports, manual exports) with timing and error tracking.

Minimal dependencies: only requires ``base``, ``web``, and ``jsonifier``.
