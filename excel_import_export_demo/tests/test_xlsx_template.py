# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from ast import literal_eval
from .test_common import TestExcelImportExport


class TestXLSXTemplate(TestExcelImportExport):

    @classmethod
    def setUpClass(cls):
        super(TestExcelImportExport, cls).setUpClass()

    def test_xlsx_tempalte(self):
        """ Test XLSX Tempalte input and output instruction """
        self.setUpXLSXTemplate()
        instruction_dict = literal_eval(self.sample_template.instruction)
        self.assertDictEqual(
            instruction_dict,
            {
                '__EXPORT__': {
                    'sale_order': {
                        '_HEAD_': {
                            'B2': 'partner_id.display_name${value or ""}'
                                  '#{align=left;style=text}#??',
                            'B3': 'name${value or ""}'
                                  '#{align=left;style=text}#??'},
                        'order_line': {
                            'A6': 'product_id.display_name${value or ""}'
                                  '#{style=text}#??',
                            'B6': 'name${value or ""}#{style=text}#??',
                            'C6': 'product_uom_qty${value or 0}'
                                  '#{style=number}#??',
                            'D6': 'product_uom.name${value or ""}'
                                  '#{style=text}#??',
                            'E6': 'price_unit${value or 0}#{style=number}#??',
                            'F6': 'tax_id${value and ",".join([x.display_name '
                                  'for x in value]) or ""}#{}#??',
                            'G6': 'price_subtotal${value or 0}'
                                  '#{style=number}#??'
                        }
                    }
                },
                '__IMPORT__': {
                    'sale_order': {
                        'order_line': {
                            'A6': 'product_id',
                            'B6': 'name',
                            'C6': 'product_uom_qty',
                            'D6': 'product_uom',
                            'E6': 'price_unit',
                            'F6': 'tax_id',
                        }
                    }
                },
                '__POST_IMPORT__': False
            }
        )
        # Finally load excel file into this new template
        self.assertFalse(self.sample_template.datas)  # Not yet loaded
        self.template_obj.load_xlsx_template([self.sample_template.id],
                                             addon='excel_import_export_demo')
        self.assertTrue(self.sample_template.datas)  # Loaded successfully
