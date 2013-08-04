# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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
import re
from openerp.addons.web.controllers.main import Database
from openerp.addons.web.common.http import jsonrequest

get_list_org = Database.get_list.__closure__[0].cell_contents

@jsonrequest
def get_list(self, req):
    db_filter = req.httprequest.environ.get('HTTP_X_OPENERP_DBFILTER', '.*')
    dbs = get_list_org(self, req)
    return {'db_list': [db for db in 
        dbs.get('db_list', [])
        if re.match(db_filter, db)]}

Database.get_list = get_list
