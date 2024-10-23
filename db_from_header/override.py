# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from odoo import http
from odoo.tools import config

db_monodb_org = http.db_monodb


def db_monodb(httprequest=None):
    res = db_monodb_org(httprequest)
    if res is None:
        dbs = http.db_list(True, httprequest)
        httprequest = httprequest or http.request.httprequest
        db = httprequest.environ.get('HTTP_X_ODOO_DB')
        if db in dbs:
            res = db
    return res


if 'db_from_header' in config.get('server_wide_modules'):
    _logger = logging.getLogger(__name__)
    _logger.info('monkey patching http.db_monodb')
    http.db_monodb = db_monodb
