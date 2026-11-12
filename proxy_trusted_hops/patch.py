# Copyright 2026 Ametras intelligence GmbH
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import configparser
import functools
import logging
import os

from werkzeug.middleware.proxy_fix import ProxyFix

from odoo import http
from odoo.tools import config

_logger = logging.getLogger(__name__)


SECTION = "proxy_trusted_hops"


def _section_options(parser):
    """Return the options of the section, with lowercase names."""
    if not parser.has_section(SECTION):
        return {}
    return {name.lower(): value for name, value in parser[SECTION].items()}


def _get_section():
    """Return the options of the ``[proxy_trusted_hops]`` section.

    Read from ``server_environment`` when it is on the addons path, otherwise
    from the Odoo configuration file, which the module reads itself: not every
    Odoo version loads sections other than ``[options]``.
    """
    try:
        from odoo.addons.server_environment import serv_config
    except ImportError:
        serv_config = None
    if serv_config is not None:
        return _section_options(serv_config)
    # Newer Odoo versions keep the path in config["config"] and deprecate
    # config.rcfile, older ones only have config.rcfile.
    path = config.get("config") or getattr(config, "rcfile", None)
    if not path:
        return {}
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(path)
    return _section_options(parser)


def _get_trusted_hops():
    """Return the number of trusted proxies in front of Odoo.

    Read from the ``ODOO_TRUSTED_PROXIES`` environment variable, or the
    ``trusted_proxies`` option of the ``[proxy_trusted_hops]`` section of the
    configuration file. Defaults to 1, which is what Odoo trusts out of the
    box.
    """
    value = os.environ.get("ODOO_TRUSTED_PROXIES") or _get_section().get(
        "trusted_proxies"
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
            "Invalid trusted_proxies value %r: it must be a positive integer. "
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
