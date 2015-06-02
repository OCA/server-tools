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
            report_view_ids = self.env.context.get('report_views', False)
            suffix = self.env.context.get('suffix', 'copy')
            report_name = values['report_name']
            module = report_name.split('.')[0]
            name = report_name.split('.')[1]
            for report_view in self.env['ir.ui.view'].browse(report_view_ids):
                origin_name = name.replace(('_%s' % suffix), '')
                new_report_name = '%s_%s' % (origin_name, suffix)
                qweb_view_data = {
                    'name': report_view.name.replace(
                        origin_name, new_report_name),
                    'mode': 'primary',
                    'type': 'qweb',
                    'arch': report_view.arch.replace(
                        origin_name, new_report_name),
                }
                qweb_view = self.env['ir.ui.view'].create(qweb_view_data)
                model_data_data = {
                    'module': module,
                    'name': report_view.name.replace(
                        origin_name, new_report_name),
                    'res_id': qweb_view.id,
                    'model': 'ir.ui.view',
                }
                self.env['ir.model.data'].create(model_data_data)
                value_view_data = {
                    'name': values['name'],
                    'model': values['model'],
                    'key2': 'client_print_multi',
                    'value_unpickle': ('ir.actions.report.xml,%s' %
                                       report_xml.id),
                }
                self.env['ir.values'].create(value_view_data)
            if not report_view_ids:
                qweb_view_data = {
                    'name': name,
                    'mode': 'primary',
                    'type': 'qweb',
                    'arch': '<?xml version="1.0"?>\n'
                            '<t t-name="%s">\n</t>' % report_name,
                }
                qweb_view = self.env['ir.ui.view'].create(qweb_view_data)
                model_data_data = {
                    'module': module,
                    'name': name,
                    'res_id': qweb_view.id,
                    'model': 'ir.ui.view',
                }
                self.env['ir.model.data'].create(model_data_data)
                value_view_data = {
                    'name': values['name'],
                    'model': values['model'],
                    'key2': 'client_print_multi',
                    'value_unpickle': (
                        'ir.actions.report.xml,%s' % report_xml.id),
                }
                self.env['ir.values'].create(value_view_data)
        return report_xml

    @api.one
    def copy(self, default=None):
        if default is None:
            default = {}
        suffix = self.env.context.get('suffix', 'copy')
        default['name'] = '%s (%s)' % (self.name, suffix)
        default['report_name'] = '%s_%s' % (self.report_name, suffix.lower())
        report_views = self.env['ir.ui.view'].search([
            ('name', 'ilike', self.report_name.split('.')[1]),
            ('type', '=', 'qweb')])
        return super(IrActionsReport,
                     self.with_context(
                         report_views=report_views.ids,
                         suffix=suffix.lower())).copy(default=default)
