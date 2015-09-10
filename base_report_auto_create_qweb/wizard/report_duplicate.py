# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import api, fields, models


class IrActionsReportDuplicate(models.TransientModel):
    _name = 'ir.actions.report.xml.duplicate'

    suffix = fields.Char(
        string='Suffix', help='This suffix will be added to the report')

    @api.one
    def duplicate_report(self):
        active_id = self.env.context.get('active_id')
        model = self.env.context.get('active_model')
        if model:
            object = self.env[model].browse(active_id)
            object.with_context(
                suffix=self.suffix, enable_duplication=True).copy()
        return {}
