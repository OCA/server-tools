# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
#    This module copyright (C) 2014 ACSONE SA/NV (<http://acsone.eu>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
