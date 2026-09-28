# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo import http
from odoo.tools import config

_logger = logging.getLogger(__name__)

db_filter_org = http.db_filter


def db_filter(dbs, host=None):
    dbs = db_filter_org(dbs, host)
    http_request = getattr(http, "request", None)
    if not http_request:
        return dbs
    httprequest = getattr(http_request, "httprequest", None)
    if not httprequest:
        return dbs
    db_filter_hdr = httprequest.environ.get("HTTP_X_ODOO_DBFILTER")
    if db_filter_hdr:
        try:
            dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
        except re.error:
            _logger.warning(
                "Invalid regex in X-Odoo-DBFilter header: %r", db_filter_hdr
            )
    return dbs


if config.get("proxy_mode") and "dbfilter_from_header" in config.get(
    "server_wide_modules"
):
    _logger.info("monkey patching http.db_filter")
    http.db_filter = db_filter
