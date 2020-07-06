# © 2013  Therp BV
# © 2014  ACSONE SA/NV
# Copyright 2018 Quartile Limited
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
from odoo import http
from odoo.addons.base.controllers import rpc
from odoo.http import request, route
from odoo.service import db
from odoo.tools import config

db_filter_header_from_xmlrpc = ''
db_filter_org = http.db_filter
list_dbs_org = db.list_dbs


class CorsRPC(rpc.RPC):
    def _check_dbfilter(self):
        # saving `HTTP_X_ODOO_DBFILTER` header for later
        environ = request.httprequest.environ
        global db_filter_header_from_xmlrpc
        db_filter_header_from_xmlrpc = ''
        if 'HTTP_X_ODOO_DBFILTER' in environ:
            db_filter_header_from_xmlrpc = environ['HTTP_X_ODOO_DBFILTER']

    @route('/xmlrpc/<service>', auth='none', methods=['POST'], csrf=False, save_session=False)
    def xmlrpc_1(self, service):
        self._check_dbfilter()
        return super(CorsRPC, self).xmlrpc_1(service)

    @route('/xmlrpc/2/<service>', auth='none', methods=['POST'], csrf=False, save_session=False)
    def xmlrpc_2(self, service):
        self._check_dbfilter()
        return super(CorsRPC, self).xmlrpc_2(service)


def db_filter(dbs, httprequest=None):
    dbs = db_filter_org(dbs, httprequest)
    httprequest = httprequest or http.request.httprequest
    db_filter_hdr = httprequest.environ.get('HTTP_X_ODOO_DBFILTER')
    # patching also `db_filter_header_from_xmlrpc` for cleaning-up in case of
    # different headers sent via xmlrpc and http
    global db_filter_header_from_xmlrpc
    db_filter_header_from_xmlrpc = db_filter_hdr
    if db_filter_hdr:
        dbs = [db for db in dbs if re.match(db_filter_hdr, db)]
    return dbs


def list_dbs(force=False):
    dbs = list_dbs_org(force)
    global db_filter_header_from_xmlrpc
    if db_filter_header_from_xmlrpc:
        dbs = [db for db in dbs if re.match(db_filter_header_from_xmlrpc, db)]
    return dbs


if config.get('proxy_mode') and \
   'dbfilter_from_header' in config.get('server_wide_modules'):
    _logger = logging.getLogger(__name__)
    _logger.info('monkey patching http.db_filter')
    http.db_filter = db_filter
    _logger.info('monkey patching db.list_dbs')
    db.list_dbs = list_dbs
