import logging

from opentelemetry.propagate import extract

from odoo.http import request

_logger = logging.getLogger(__name__)


def _is_trusted_inbound_request():
    try:
        return bool(getattr(request, "uid", None))
    except Exception:
        return False


def extract_context():
    if not _is_trusted_inbound_request():
        return None

    try:
        headers = request.httprequest.headers
        ctx = extract(headers)
        return ctx
    except Exception:
        _logger.exception("Failed to extract inbound trace context")
        return None
