# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import Form

from .test_common import TestExcelImportExport


class TestXLSXImportExport(TestExcelImportExport):
    @classmethod
    def setUpClass(cls):
        super(TestExcelImportExport, cls).setUpClass()

    def test_xlsx_export_import(self):
        """Test Export Excel from Sales Order"""
        # Create Sales Order
        self.setUpSaleOrder()
        # ----------- EXPORT ---------------
        ctx = {
            "active_model": "sale.order",
            "active_ids": [self.sale_order.id],
            "template_domain": [
                ("res_model", "=", "sale.order"),
                ("fname", "=", "sale_order.xlsx"),
                ("gname", "=", False),
            ],
        }
        f = Form(self.env["export.xlsx.wizard"].with_context(**ctx))
        export_wizard = f.save()
        # Test whether it loads correct template
        self.assertEqual(
            export_wizard.template_id,
            self.env.ref("excel_import_export_demo.sale_order_xlsx_template"),
        )
        # Export excel
        export_wizard.action_export()
        self.assertTrue(export_wizard.data)
        self.export_file = export_wizard.data

        # ----------- IMPORT ---------------
        ctx = {
            "active_model": "sale.order",
            "active_id": self.sale_order.id,
            "template_domain": [
                ("res_model", "=", "sale.order"),
                ("fname", "=", "sale_order.xlsx"),
                ("gname", "=", False),
            ],
            "template_context": {"state": "draft"},
        }
        with Form(self.env["import.xlsx.wizard"].with_context(**ctx)) as f:
            f.import_file = self.export_file
        import_wizard = f.save()
        # Test sample template
        import_wizard.get_import_sample()
        self.assertTrue(import_wizard.datas)
        # Test whether it loads correct template
        self.assertEqual(
            import_wizard.template_id,
            self.env.ref("excel_import_export_demo.sale_order_xlsx_template"),
        )
        # Import Excel
        import_wizard.action_import()

    def test_add_remove_export_import_action(self):
        """On the template itself, test add / remove action"""
        template = self.env.ref("excel_import_export_demo.sale_order_xlsx_template")
        self.assertTrue(template.import_action_id)
        self.assertTrue(template.export_action_id)
        # Remove actions
        template.remove_export_action()
        template.remove_import_action()
        self.assertFalse(template.import_action_id)
        self.assertFalse(template.export_action_id)
        # Add actions back again
        template.add_export_action()
        template.add_import_action()
        self.assertTrue(template.import_action_id)
        self.assertTrue(template.export_action_id)
