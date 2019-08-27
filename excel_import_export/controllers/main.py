# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import json
import base64
import time
from odoo.addons.web.controllers import main as report
from odoo.http import content_disposition, route, request
from odoo.tools.safe_eval import safe_eval


class ReportController(report.ReportController):

    @route()
    def report_routes(self, reportname, docids=None, converter=None, **data):
        if converter == 'excel':
            report = request.env['ir.actions.report']._get_report_from_name(
                reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(',')]
            if data.get('options'):
                data.update(json.loads(data.pop('options')))
            if data.get('context'):
                # Ignore 'lang' here, because the context in data is the one
                # from the webclient *but* if the user explicitely wants to
                # change the lang, this mechanism overwrites it.
                data['context'] = json.loads(data['context'])
                if data['context'].get('lang'):
                    del data['context']['lang']
                context.update(data['context'])
            excel, report_name = report.with_context(context).render_excel(
                docids, data=data
            )
            excel = base64.decodestring(excel)
            if report.print_report_name and not len(docids) > 1:
                obj = request.env[report.model].browse(docids[0])
                file_ext = report_name.split('.')[-1:].pop()
                report_name = safe_eval(report.print_report_name,
                                        {'object': obj, 'time': time})
                report_name = '%s.%s' % (report_name, file_ext)
            excelhttpheaders = [
                ('Content-Type', 'application/vnd.openxmlformats-'
                                 'officedocument.spreadsheetml.sheet'),
                ('Content-Length', len(excel)),
                (
                    'Content-Disposition',
                    content_disposition(report_name)
                )
            ]
            return request.make_response(excel, headers=excelhttpheaders)
        return super(ReportController, self).report_routes(
            reportname, docids, converter, **data
        )
