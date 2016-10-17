# -*- coding: utf-8 -*-
# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from odoo import http

db_filter_org = http.db_filter


def db_filter(dbs, httprequest=None):
    dbs = db_filter_org(dbs, httprequest)
    httprequest = httprequest or http.request.httprequest
    db_filter_hdr = httprequest.environ.get('HTTP_X_ODOO_DBFILTER')
    if db_filter_hdr:
        dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
    return dbs

http.db_filter = db_filter
