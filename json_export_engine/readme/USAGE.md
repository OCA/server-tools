# API Reference

## REST API Endpoints

Each configured endpoint exposes two URLs:

- **Data URL**: `GET /api/json_export/<route_path>`
- **Schema URL**: `GET /api/json_export/<route_path>/schema`

## Authentication

Three authentication modes are supported per endpoint:

| Mode | Header | Description |
|------|--------|-------------|
| `none` | — | No authentication required |
| `api_key` | `X-API-Key: <key>` | API key validated via constant-time comparison |
| `user` | Session cookie | Requires an active Odoo user session |

```bash
# API Key example
curl -H "X-API-Key: YOUR_KEY" https://odoo.example.com/api/json_export/products
```

## Pagination

Paginated endpoints return results in pages. Control pagination with query
parameters:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `page` | `?page=2` | Page number (1-based) |
| `page` | `?page=last` | Jump to the last page |

The response includes a `pagination` object with navigation links:

```json
{
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 243,
    "pages": 5,
    "first": "/api/json_export/products?page=1",
    "last": "/api/json_export/products?page=5",
    "next": "/api/json_export/products?page=2",
    "prev": null
  }
}
```

## Filtering

When `allow_filtering` is enabled on the endpoint, use
`?filter[field][operator]=value` query parameters. Multiple filters compose
with AND logic.

**Supported operators:**

| Operator | SQL equivalent | Example |
|----------|---------------|---------|
| `eq` | `=` | `?filter[name][eq]=Acme` |
| `ne` | `!=` | `?filter[status][ne]=draft` |
| `like` | `like` | `?filter[name][like]=Acme%` |
| `ilike` | `ilike` | `?filter[name][ilike]=acme` |
| `gt` | `>` | `?filter[amount][gt]=100` |
| `gte` | `>=` | `?filter[amount][gte]=100` |
| `lt` | `<` | `?filter[amount][lt]=500` |
| `lte` | `<=` | `?filter[amount][lte]=500` |
| `in` | `in` | `?filter[state][in]=draft,confirmed` |

Only fields included in the export schema parser can be used for filtering.
Attempting to filter on other fields returns a 400 error.

```bash
curl "https://odoo.example.com/api/json_export/products?filter[name][ilike]=widget&filter[qty][gt]=0"
```

## Sorting

When `allow_sorting` is enabled, use `?sort=field1,-field2` to control the
order. Prefix a field name with `-` for descending order.

```bash
curl "https://odoo.example.com/api/json_export/products?sort=-create_date,name"
```

## Field Selection

When `allow_field_selection` is enabled, use `?fields=field1,field2` to return
only a subset of fields. Requesting a field not in the schema parser returns
a 400 error.

```bash
curl "https://odoo.example.com/api/json_export/products?fields=id,name,price"
```

## Response Format

### Success (200)

```json
{
  "success": true,
  "data": [ ... ],
  "pagination": { ... },
  "meta": {
    "schema": "Products",
    "model": "product.template",
    "duration_ms": 42
  }
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": 400,
    "message": "Field 'password' is not allowed for filtering."
  }
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (invalid filter, sort, or fields parameter) |
| 401 | Unauthorized (missing or invalid credentials) |
| 404 | Endpoint not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

## Rate Limiting

When `rate_limit` is enabled on an endpoint, the server enforces a
sliding-window rate limit per client IP address.

- **`rate_limit_count`** — maximum requests allowed per window (default: 60)
- **`rate_limit_window`** — window duration in seconds (default: 60)

When the limit is exceeded, the API returns:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 12
Content-Type: application/json

{"success": false, "error": {"code": 429, "message": "Rate limit exceeded. Try again later."}}
```

**Limitation:** The rate limit store is in-memory per worker process. In a
multi-process deployment, each worker tracks limits independently. For
strict global rate limiting, use a reverse proxy (e.g., nginx `limit_req`).

## Webhook Payload

When a webhook fires, it sends a POST request with the following structure:

```json
{
  "event": "create",
  "model": "res.partner",
  "schema": "Partners",
  "timestamp": "2026-01-15T10:30:00",
  "delivery_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "records": [ ... ]
}
```

### Headers

| Header | Description |
|--------|-------------|
| `Content-Type` | `application/json` |
| `X-Delivery-ID` | Unique UUID for deduplication — same across retries |
| `X-Webhook-Signature` | HMAC-SHA256 hex digest (when `secret_key` is set) |

### Deduplication

Each webhook delivery is assigned a unique `delivery_id` (UUID v4). This ID
is included both in the JSON payload and as the `X-Delivery-ID` HTTP header.
The same `delivery_id` is preserved across all retry attempts, allowing
consumers to detect and discard duplicate deliveries.

### Signature Verification

When a `secret_key` is configured, verify the signature:

```python
import hmac, hashlib

expected = hmac.new(
    secret_key.encode(),
    request_body,
    hashlib.sha256,
).hexdigest()

assert hmac.compare_digest(expected, request.headers["X-Webhook-Signature"])
```

## Async Support (queue_job)

When the `queue_job` module is installed, webhook deliveries and scheduled
exports can be processed asynchronously via background jobs.

- **Webhooks**: Enable `async_delivery` on a webhook record. Deliveries will
  be enqueued via `with_delay()` instead of executing inline.
- **Schedules**: Enable `async_export` on a schedule record. The cron entry
  point will enqueue `_run_scheduled_export()` as a background job.

When `queue_job` is **not** installed, these flags have no effect and
processing falls back to synchronous execution.

## Log Autovacuum

Export log entries accumulate over time. The module includes an autovacuum
mechanism to clean up old records.

### Configuration

Set the retention period via the system parameter:

    json_export_engine.log_retention_days = 90

The default retention is **90 days**.

### Activation

The autovacuum cron job (`JSON Export: Log Autovacuum`) is **inactive by
default**. To enable it:

1. Go to **Settings > Technical > Automation > Scheduled Actions**
2. Find *JSON Export: Log Autovacuum*
3. Set it to **Active**

The cron runs daily and deletes log entries older than the configured
retention period in batches.

## Example curl Commands

```bash
# List all partners (no auth)
curl https://odoo.example.com/api/json_export/demo-partners

# With API key
curl -H "X-API-Key: abc123" https://odoo.example.com/api/json_export/products

# Page 2
curl "https://odoo.example.com/api/json_export/demo-partners?page=2"

# Filter + sort + field selection
curl "https://odoo.example.com/api/json_export/demo-partners?filter[name][ilike]=acme&sort=-name&fields=id,name,email"

# Get JSON schema
curl https://odoo.example.com/api/json_export/demo-partners/schema
```
