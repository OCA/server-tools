# Copyright 2026 Akretion France (https://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

import odoo.http
from odoo.tools import config

_logger = logging.getLogger(__name__)


def post_load_hook():
    """Hide Python tracebacks in JSON-RPC error responses."""
    original_serialize_exception = odoo.http.serialize_exception

    def serialize_exception(*args, **kwargs):
        result = original_serialize_exception(*args, **kwargs)
        if not config["dev_mode"]:
            result["debug"] = ""
        return result

    odoo.http.serialize_exception = serialize_exception
    _logger.info("Patched odoo.http.serialize_exception to hide tracebacks")
