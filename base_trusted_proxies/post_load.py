# Copyright 2026 ACSONE SA/NV (<http://acsone.eu>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import functools
import logging
import os

from odoo import http, tools

_logger = logging.getLogger(__name__)


def post_load():
    if tools.config["test_enable"]:
        return
    trusted_proxies_env_var = os.environ.get("ODOO_TRUSTED_PROXIES")
    if not trusted_proxies_env_var:
        _logger.warning(
            "Missing configuration for module 'base_trusted_proxies': "
            "'ODOO_TRUSTED_PROXIES' environment variable."
        )
        return
    if not trusted_proxies_env_var.isdigit():
        _logger.warning(
            "'ODOO_TRUSTED_PROXIES' environment variable must be a positive integer."
        )
        return

    trusted_proxies_nbr = int(trusted_proxies_env_var)
    if trusted_proxies_nbr < 1:
        _logger.warning(
            "'ODOO_TRUSTED_PROXIES' environment variable must be a positive integer."
        )
        return

    _logger.info(
        f"Patch ProxyFix to trust {trusted_proxies_nbr} proxies in X-Forwarded-For."
    )

    from werkzeug.middleware.proxy_fix import ProxyFix as ProxyFix_

    http.ProxyFix = functools.partial(
        ProxyFix_, x_for=trusted_proxies_nbr, x_proto=1, x_host=1
    )
