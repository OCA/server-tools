# -*- coding: utf-8 -*-
# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
from openerp import http
from openerp.tools import config

db_filter_org = http.db_filter


def db_filter(dbs, httprequest=None):
    dbs = db_filter_org(dbs, httprequest)
    httprequest = httprequest or http.request.httprequest
    db_filter_hdr_odoo = httprequest.environ.get('HTTP_X_ODOO_DBFILTER')
    db_filter_hdr_openerp = httprequest.environ.get('HTTP_X_OPENERP_DBFILTER')
    if db_filter_hdr_odoo and db_filter_hdr_openerp:
        raise RuntimeError("x-odoo-dbfilter and x-openerp-dbfiter "
                           "are both set")
    db_filter_hdr = db_filter_hdr_odoo or db_filter_hdr_openerp
    if db_filter_hdr:
        dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
    return dbs

if config.get('proxy_mode') and \
   'dbfilter_from_header' in config.get('server_wide_modules'):
    _logger = logging.getLogger(__name__)
    _logger.info('monkey patching http.db_filter')
    http.db_filter = db_filter
