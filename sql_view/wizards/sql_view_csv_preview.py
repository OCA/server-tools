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

import base64
from StringIO import StringIO

try:
    import unicodecsv
except ImportError:
    unicodecsv = None

from openerp.osv import orm, fields
from openerp.tools.translate import _


class SQLViewCSVPreview(orm.TransientModel):
    _name = 'sql.view.csv.preview'
    _description = 'SQL View CSV Preview'

    _columns = {
        'limit': fields.integer(string='Limit',
                                help='Number of records. 0 means infinite.'),
        'data': fields.binary('CSV', readonly=True),
        'filename': fields.char('File Name', readonly=True),
    }

    _defaults = {
        'filename': 'csv-preview.csv',
        'limit': 100,
    }

    def _query(self, cr, uid, form, sql_view, context=None):
        view_name = sql_view.complete_sql_name
        query = "SELECT * FROM {view_name} "
        if form.limit:
            query += "LIMIT {limit}"
        return query.format(view_name=view_name, limit=form.limit)

    def export_csv(self, cr, uid, ids, context=None):
        if context is None:
            return
        sql_view_ids = context.get('active_ids', [])
        assert len(ids) == 1, "1 wizard ID expected"
        assert len(sql_view_ids) == 1, "1 active ID expected"

        form = self.browse(cr, uid, ids[0], context=context)
        sql_view = self.pool['sql.view'].browse(cr, uid, sql_view_ids[0],
                                                context=context)
        query = self._query(cr, uid, form, sql_view, context=context)
        cr.execute(query)
        headers = [desc[0] for desc in cr.description]
        records = cr.fetchall()
        filedata = StringIO()
        if not unicodecsv:
            raise orm.except_orm(
                _('Error'), _('Please install the unicodecsv library'))
        try:
            writer = unicodecsv.writer(filedata, encoding='utf-8')
            writer.writerow(headers)
            writer.writerows(records)
            form.write({'data': base64.encodestring(filedata.getvalue())})
        finally:
            filedata.close()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': ids[0],
            'views': [(False, 'form')],
            'target': 'new',
        }
