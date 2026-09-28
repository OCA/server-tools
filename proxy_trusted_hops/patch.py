# Copyright 2026 Ametras intelligence GmbH
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import functools
import logging
import os

from werkzeug.middleware.proxy_fix import ProxyFix

from odoo import http
from odoo.tools import config

_logger = logging.getLogger(__name__)


def _get_trusted_hops():
    """Return the number of trusted proxies in front of Odoo.

    Read from the ``proxy_trusted_hops`` option of the configuration file,
    or the ``ODOO_PROXY_TRUSTED_HOPS`` environment variable. Defaults to 1,
    which is what Odoo trusts out of the box.
    """
    value = config.get("proxy_trusted_hops") or os.environ.get(
        "ODOO_PROXY_TRUSTED_HOPS"
    )
    if not value:
        return 1
    try:
        hops = int(value)
        if hops < 1:
            raise ValueError
    except ValueError:
        # A wrong value must never make the client address spoofable, so fall
        # back to the core behavior instead of guessing.
        _logger.error(
            "Invalid proxy_trusted_hops value %r: it must be a positive integer. "
            "Only the last proxy is trusted.",
            value,
        )
        return 1
    return hops


def post_load():
    hops = _get_trusted_hops()
    if hops == 1:
        return
    # odoo.http looks up ProxyFix on each request, so replacing the module
    # attribute is enough. Protocol and host keep the core setting, only the
    # client address resolution changes.
    http.ProxyFix = functools.partial(ProxyFix, x_for=hops, x_proto=1, x_host=1)
    _logger.info("Trusting %s proxies for the X-Forwarded-For header.", hops)
