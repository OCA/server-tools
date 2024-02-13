# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
from odoo import http
from odoo.tools import config

db_filter_org = http.db_filter


def db_filter(dbs, httprequest=None):
    dbs = db_filter_org(dbs, httprequest)
    httprequest = httprequest or http.request.httprequest
    db_filter_hdr = httprequest.environ.get('HTTP_X_ODOO_DBFILTER', '')

    # copied from original db_filter function, to support '%h' and '%d'
    h = httprequest.environ.get('HTTP_HOST', '').split(':')[0]
    d, _, r = h.partition('.')
    if d == "www" and r:
        d = r.partition('.')[0]
    d, h = re.escape(d), re.escape(h)
    db_filter_hdr = db_filter_hdr.replace('%h', h).replace('%d', d)

    if db_filter_hdr:
        dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
    return dbs


if config.get('proxy_mode') and \
   'dbfilter_from_header' in config.get('server_wide_modules'):
    _logger = logging.getLogger(__name__)
    _logger.info('monkey patching http.db_filter')
    http.db_filter = db_filter
