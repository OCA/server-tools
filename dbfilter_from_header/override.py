# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re

from odoo.http import router
from odoo.tools import config

db_filter_org = router.db_filter


def db_filter(dbs, host=None):
    dbs = db_filter_org(dbs, host)
    httprequest = router.request.httprequest
    db_filter_hdr = httprequest.environ.get("HTTP_X_ODOO_DBFILTER")
    if db_filter_hdr:
        dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
    return dbs


if config.get("proxy_mode") and "dbfilter_from_header" in config.get(
    "server_wide_modules"
):
    _logger = logging.getLogger(__name__)
    _logger.info("monkey patching http.router.db_filter")
    router.db_filter = db_filter
