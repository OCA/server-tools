# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import http
from odoo.tools import config

from .override import db_filter


def post_load():
    if config.get("proxy_mode") and "dbfilter_from_header" in config.get(
        "server_wide_modules"
    ):
        _logger = logging.getLogger(__name__)
        _logger.info("monkey patching http.db_filter")
        http.db_filter = db_filter
