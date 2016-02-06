# -*- coding: utf-8 -*-
# (c) 2016 Tony Galmiche / InfoSaône
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
try:
    import json
except ImportError:
    import simplejson as json

import openerp.http as http
from openerp.http import request
from openerp.addons.web.controllers.main import CSVExport


class CSVExportView(CSVExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(CSVExportView, self).__getattribute__(name)

    @http.route('/web/export/csv_view', type='http', auth='user')
    def export_csv_view(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        columns_headers = data.get('headers', [])
        rows = data.get('rows', [])

        return request.make_response(
            self.from_data(columns_headers, rows),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
