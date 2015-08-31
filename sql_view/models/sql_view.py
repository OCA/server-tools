# -*- coding: utf-8 -*-
#
#
#    Authors: Guewen Baconnier
#    Copyright 2015 Camptocamp SA
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
#

import re
from openerp.osv import orm, fields

# views are created with a prefix to prevent conflicts
SQL_VIEW_PREFIX = u'sql_view_'
# 63 chars is the length of a postgres identifier
USER_NAME_SIZE = 63 - len(SQL_VIEW_PREFIX)

PG_NAME_RE = re.compile(r'^[a-z_][a-z0-9_$]*$', re.I)


class sql_view(orm.Model):
    _name = 'sql.view'

    _columns = {
        'name': fields.char(string='View Name', required=True),
        'sql_name': fields.char(string='SQL Name', required=True,
                                size=USER_NAME_SIZE),
        'definition': fields.text(string='Definition', required=True),
    }

    def _check_sql_name(self, cr, uid, ids, context=None):
        records = self.browse(cr, uid, ids, context=context)
        return all(PG_NAME_RE.match(record.sql_name) for record in records)

    _constraints = [
        (_check_sql_name,
         'The SQL name is not a valid PostgreSQL identifier',
         ['sql_name']),
    ]
