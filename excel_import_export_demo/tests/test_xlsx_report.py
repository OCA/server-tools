# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from .test_common import TestExcelImportExport


class TestXLSXReport(TestExcelImportExport):

    @classmethod
    def setUpClass(cls):
        super(TestXLSXReport, cls).setUpClass()

    def test_xlsx_report(self):
        """ Test Report from Sales Order """
        # Create Many Sales Orders
        self.setUpManySaleOrder()
        ctx = {'template_domain': [('res_model', '=', 'report.sale.order'),
                                   ('fname', '=', 'report_sale_order.xlsx'),
                                   ('gname', '=', False)], }
        Wizard = self.env['report.sale.order']
        defaults = Wizard.with_context(ctx).default_get({})
        report_wizard = Wizard.create({
            'partner_id': self.partner.id,
            'template_id': defaults.get('template_id')})
        # Test whether it loads correct template
        self.assertEqual(report_wizard.template_id,
                         self.env.ref('excel_import_export_demo.'
                                      'report_sale_order_template'))
        # Report excel
        report_wizard.report_xlsx()
        self.assertTrue(report_wizard.data)
