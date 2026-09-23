# Copyright 2026 KOBROS-TECH LTD (https://kobros-tech.com).
# @author Mohamed Alkobrosli <mohamed@kobros-tech.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import hmac
import json
import math
import threading
import time

from werkzeug.urls import url_encode

from odoo import http
from odoo.http import Response, request

# In-memory sliding-window rate limiter (per-worker in multi-process).
_rate_limit_store = {}
_rate_limit_lock = threading.Lock()


def _check_rate_limit(endpoint_id, ip, max_count, window_seconds):
    """Check whether a request is within the rate limit.

    Returns ``(allowed, retry_after)`` where *retry_after* is the number
    of seconds the client should wait (0 when allowed).
    """
    now = time.time()
    key = (endpoint_id, ip)
    with _rate_limit_lock:
        timestamps = _rate_limit_store.get(key, [])
        cutoff = now - window_seconds
        # Prune expired entries
        timestamps = [t for t in timestamps if t > cutoff]
        if len(timestamps) >= max_count:
            retry_after = int(timestamps[0] - cutoff) + 1
            _rate_limit_store[key] = timestamps
            return False, retry_after
        timestamps.append(now)
        _rate_limit_store[key] = timestamps
        # Periodically evict stale keys to prevent unbounded memory growth
        if len(_rate_limit_store) > 10000:
            stale = [
                k for k, v in _rate_limit_store.items() if not v or v[-1] <= cutoff
            ]
            for k in stale:
                del _rate_limit_store[k]
        return True, 0


class JsonExportController(http.Controller):
    @http.route(
        "/api/json_export/<path:path>",
        type="http",
        auth="public",
        methods=["GET", "OPTIONS"],
        csrf=False,
    )
    def export_data(self, path, **kwargs):
        # Handle CORS preflight
        endpoint = self._find_endpoint(path)
        if not endpoint:
            return self._error_response(404, "Endpoint not found")

        if request.httprequest.method == "OPTIONS":
            return self._cors_preflight(endpoint)

        # Authenticate
        auth_error = self._check_auth(endpoint)
        if auth_error:
            return auth_error

        # Rate limiting
        if endpoint.rate_limit:
            ip = request.httprequest.remote_addr
            allowed, retry_after = _check_rate_limit(
                endpoint.id, ip, endpoint.rate_limit_count, endpoint.rate_limit_window
            )
            if not allowed:
                return self._rate_limit_response(retry_after)

        schema = endpoint.schema_id
        start_time = time.time()

        try:
            params = request.httprequest.args
            qp = self._process_query_params(endpoint, schema, params)

            records, pagination = self._fetch_paginated_records(
                schema,
                endpoint,
                path,
                params,
                kwargs,
                qp["extra_domain"],
                qp["order"],
            )

            if qp["custom_parser"]:
                data = schema.sudo()._serialize_records_with_parser(
                    records, qp["custom_parser"]
                )
            else:
                data = schema.sudo()._serialize_records(records)

            duration = int((time.time() - start_time) * 1000)

            response_data = {
                "success": True,
                "data": data,
                "pagination": pagination,
                "meta": {
                    "schema": schema.name,
                    "model": schema.model_name,
                    "duration_ms": duration,
                },
            }

            self._log_api_success(
                schema,
                endpoint,
                path,
                pagination,
                duration,
                len(data),
                qp["filter_info"],
                qp["sort_info"],
                qp["fields_info"],
            )

            return self._json_response(response_data, endpoint)

        except ValueError as e:
            duration = int((time.time() - start_time) * 1000)
            schema.sudo()._create_log("api", "error", 0, duration, error_message=str(e))
            return self._error_response(400, str(e))

        except Exception as e:
            duration = int((time.time() - start_time) * 1000)
            schema.sudo()._create_log("api", "error", 0, duration, error_message=str(e))
            return self._error_response(500, "Internal server error")

    @http.route(
        "/api/json_export/<path:path>/schema",
        type="http",
        auth="public",
        methods=["GET", "OPTIONS"],
        csrf=False,
    )
    def export_schema(self, path, **kwargs):
        """Serve the JSON Schema for an endpoint."""
        endpoint = self._find_endpoint(path)
        if not endpoint:
            return self._error_response(404, "Endpoint not found")

        if request.httprequest.method == "OPTIONS":
            return self._cors_preflight(endpoint)

        auth_error = self._check_auth(endpoint)
        if auth_error:
            return auth_error

        # Rate limiting
        if endpoint.rate_limit:
            ip = request.httprequest.remote_addr
            allowed, retry_after = _check_rate_limit(
                endpoint.id, ip, endpoint.rate_limit_count, endpoint.rate_limit_window
            )
            if not allowed:
                return self._rate_limit_response(retry_after)

        schema = endpoint.schema_id
        try:
            record_schema = schema.sudo()._generate_json_schema()
            api_schema = schema.sudo()._wrap_api_response_schema(
                record_schema, endpoint=endpoint
            )
            return self._json_response(api_schema, endpoint)
        except Exception:
            return self._error_response(500, "Failed to generate schema")

    def _process_query_params(self, endpoint, schema, params):
        """Process filtering, sorting and field selection query parameters."""
        result = {
            "extra_domain": [],
            "order": None,
            "custom_parser": None,
            "filter_info": None,
            "sort_info": None,
            "fields_info": None,
        }
        if not (
            endpoint.allow_filtering
            or endpoint.allow_sorting
            or endpoint.allow_field_selection
        ):
            return result

        allowed_fields = schema.sudo()._get_allowed_query_fields()

        if endpoint.allow_filtering:
            result["extra_domain"] = schema.sudo()._build_filter_domain(
                params, allowed_fields
            )
            if result["extra_domain"]:
                result["filter_info"] = str(result["extra_domain"])

        if endpoint.allow_sorting and params.get("sort"):
            result["order"] = schema.sudo()._build_sort_order(
                params["sort"], allowed_fields
            )
            result["sort_info"] = params["sort"]

        if endpoint.allow_field_selection and params.get("fields"):
            result["custom_parser"] = schema.sudo()._filter_parser(params["fields"])
            result["fields_info"] = params["fields"]

        return result

    def _fetch_paginated_records(
        self, schema, endpoint, path, params, kwargs, extra_domain, order
    ):
        """Fetch records with optional pagination.

        Returns (records, pagination_dict).
        """
        domain = schema._get_domain()
        if extra_domain:
            domain = domain + extra_domain
        model = request.env[schema.model_name].sudo()
        total = model.search_count(domain)

        base_path = f"/api/json_export/{path.strip('/')}"
        preserved_qs = self._build_preserved_query_string(params)

        if endpoint.paginate:
            page_size = max(endpoint.page_size, 1)
            total_pages = math.ceil(total / page_size) if total else 1

            raw_page = kwargs.get("page", "1")
            if str(raw_page).lower() == "last":
                page = total_pages
            else:
                page = min(max(int(raw_page), 1), total_pages)

            offset = (page - 1) * page_size
            records = schema.sudo()._get_records(
                limit=page_size,
                offset=offset,
                extra_domain=extra_domain or None,
                order=order,
            )

            nav = {
                "first": f"{base_path}?page=1{preserved_qs}",
                "last": f"{base_path}?page={total_pages}{preserved_qs}",
                "next": (
                    f"{base_path}?page={page + 1}{preserved_qs}"
                    if page < total_pages
                    else None
                ),
                "prev": (
                    f"{base_path}?page={page - 1}{preserved_qs}" if page > 1 else None
                ),
            }
        else:
            page_size = total
            page = 1
            total_pages = 1
            nav = {}
            records = schema.sudo()._get_records(
                no_limit=True,
                extra_domain=extra_domain or None,
                order=order,
            )

        pagination = {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": total_pages,
            **nav,
        }
        return records, pagination

    def _log_api_success(
        self,
        schema,
        endpoint,
        path,
        pagination,
        duration,
        count,
        filter_info,
        sort_info,
        fields_info,
    ):
        """Log a successful API request."""
        log_info = {
            "endpoint": endpoint.name,
            "path": path,
            "page": pagination["page"],
            "page_size": pagination["page_size"],
        }
        if filter_info:
            log_info["filter"] = filter_info
        if sort_info:
            log_info["sort"] = sort_info
        if fields_info:
            log_info["fields"] = fields_info

        schema.sudo()._create_log(
            "api",
            "success",
            count,
            duration,
            request_info=json.dumps(log_info),
        )

    def _find_endpoint(self, path):
        """Lookup active endpoint by route path."""
        path = path.strip("/")
        return (
            request.env["json.export.endpoint"]
            .sudo()
            .search(
                [
                    ("active", "=", True),
                    ("route_path", "=", path),
                    ("schema_id.active", "=", True),
                ],
                limit=1,
            )
        )

    def _check_auth(self, endpoint):
        """Validate authentication. Returns error response or None."""
        if endpoint.auth_type == "none":
            return None

        if endpoint.auth_type == "api_key":
            api_key = request.httprequest.headers.get("X-API-Key")
            if (
                not api_key
                or not endpoint.api_key
                or not hmac.compare_digest(api_key, endpoint.api_key)
            ):
                return self._error_response(401, "Invalid or missing API key")
            return None

        if endpoint.auth_type == "user":
            if request.env.user._is_public():
                return self._error_response(
                    401, "Authentication required. Please log in."
                )
            return None

        return self._error_response(403, "Unknown authentication type")

    @staticmethod
    def _build_preserved_query_string(params):
        """Rebuild all query params except 'page' into a string fragment.

        Returns a string like "&sort=-name&fields=id,name" (with leading &)
        or an empty string if there are no extra params.
        """
        preserved = {k: v for k, v in params.items() if k != "page"}
        if not preserved:
            return ""
        return "&" + url_encode(preserved)

    def _json_response(self, data, endpoint=None):
        """Build a JSON HTTP response with optional CORS headers."""
        body = json.dumps(data, ensure_ascii=False)
        headers = {"Content-Type": "application/json"}
        if endpoint and endpoint.cors_origin:
            headers.update(self._cors_headers(endpoint))
        return Response(body, status=200, headers=headers)

    def _rate_limit_response(self, retry_after):
        """Build a 429 Too Many Requests response."""
        body = json.dumps(
            {
                "success": False,
                "error": {
                    "code": 429,
                    "message": "Rate limit exceeded. Try again later.",
                },
            },
            ensure_ascii=False,
        )
        return Response(
            body,
            status=429,
            headers={
                "Content-Type": "application/json",
                "Retry-After": str(retry_after),
            },
        )

    def _error_response(self, code, message):
        """Build a JSON error response."""
        body = json.dumps(
            {"success": False, "error": {"code": code, "message": message}},
            ensure_ascii=False,
        )
        return Response(body, status=code, headers={"Content-Type": "application/json"})

    def _cors_preflight(self, endpoint):
        """Handle CORS OPTIONS preflight request."""
        headers = self._cors_headers(endpoint)
        headers["Access-Control-Max-Age"] = "86400"
        return Response("", status=204, headers=headers)

    def _cors_headers(self, endpoint):
        """Build CORS headers dict."""
        origin = endpoint.cors_origin or ""
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-API-Key",
        }
