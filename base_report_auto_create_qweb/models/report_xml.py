# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, api, exceptions, _


class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report.xml'

    @api.model
    def create(self, values):
        if (values.get('report_type') in ['qweb-pdf', 'qweb-html'] and
                values.get('report_name') and
                values['report_name'].find('.') == -1):
            raise exceptions.Warning(
                _("Template Name must contain at least a dot in it's name"))
        report_xml = super(IrActionsReport, self).create(values)
        if values.get('report_type') in ['qweb-pdf', 'qweb-html']:
            qweb_view_data = {
                'name': values['report_name'].split('.')[1],
                'mode': 'primary',
                'type': 'qweb',
                'arch': '<?xml version="1.0"?>\n'
                        '<t t-name="%s">\n</t>' % values['report_name'],
            }
            qweb_view = self.env['ir.ui.view'].create(qweb_view_data)
            model_data_data = {
                'module': values['report_name'].split('.')[0],
                'name': values['report_name'].split('.')[1],
                'res_id': qweb_view.id,
                'model': 'ir.ui.view',
            }
            self.env['ir.model.data'].create(model_data_data)
            value_view_data = {
                'name': values['name'],
                'model': values['model'],
                'key2': 'client_print_multi',
                'value_unpickle': 'ir.actions.report.xml,%s' % report_xml.id,
            }
            self.env['ir.values'].create(value_view_data)
        return report_xml
