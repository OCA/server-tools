# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from .test_common import TestExcelImportExport


class TestXLSXImportExport(TestExcelImportExport):

    @classmethod
    def setUpClass(cls):
        super(TestExcelImportExport, cls).setUpClass()

    def test_xlsx_export_import(self):
        """ Test Export Excel from Sales Order """
        # Create Sales Order
        self.setUpSaleOrder()
        # ----------- EXPORT ---------------
        ctx = {'active_model': 'sale.order',
               'active_id': self.sale_order.id,
               'template_domain': [('res_model', '=', 'sale.order'),
                                   ('fname', '=', 'sale_order.xlsx'),
                                   ('gname', '=', False)], }
        Wizard = self.env['export.xlsx.wizard'].with_context(ctx)
        defaults = Wizard.default_get({})
        export_wizard = Wizard.create({
            'template_id': defaults.get('template_id'),
            'res_id': defaults.get('res_id'),
            'res_model': defaults.get('res_model'), })
        # Test whether it loads correct template
        self.assertEqual(export_wizard.template_id,
                         self.env.ref('excel_import_export_demo.'
                                      'sale_order_xlsx_template'))
        # Export excel
        export_wizard.action_export()
        self.assertTrue(export_wizard.data)
        self.export_file = export_wizard.data

        # ----------- IMPORT ---------------
        ctx = {'active_model': 'sale.order',
               'active_id': self.sale_order.id,
               'template_domain': [('res_model', '=', 'sale.order'),
                                   ('fname', '=', 'sale_order.xlsx'),
                                   ('gname', '=', False)],
               'template_context': {'state': 'draft'}, }

        Wizard = self.env['import.xlsx.wizard'].with_context(ctx)
        defaults = Wizard.default_get({})
        import_wizard = Wizard.create({
            'import_file': self.export_file,
            'template_id': defaults.get('template_id'),
            'res_id': defaults.get('res_id'),
            'res_model': defaults.get('res_model'), })
        # Test sample template
        import_wizard.get_import_sample()
        self.assertTrue(import_wizard.datas)
        # Test whether it loads correct template
        self.assertEqual(import_wizard.template_id,
                         self.env.ref('excel_import_export_demo.'
                                      'sale_order_xlsx_template'))
        # Import Excel
        import_wizard.action_import()
