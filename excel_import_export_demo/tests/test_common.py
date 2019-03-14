# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests.common import SingleTransactionCase


class TestExcelImportExport(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestExcelImportExport, cls).setUpClass()

    @classmethod
    def setUpXLSXTemplate(cls):
        cls.template_obj = cls.env['xlsx.template']
        # Create xlsx.template using input_instruction
        input_instruction = {
            '__EXPORT__': {
                'sale_order': {
                    '_HEAD_': {
                        'B2': 'partner_id.display_name${value or ""}'
                              '#{align=left;style=text}',
                        'B3': 'name${value or ""}#{align=left;style=text}',
                    },
                    'order_line': {
                        'A6': 'product_id.display_name${value or ""}'
                              '#{style=text}',
                        'B6': 'name${value or ""}#{style=text}',
                        'C6': 'product_uom_qty${value or 0}#{style=number}',
                        'D6': 'product_uom.name${value or ""}#{style=text}',
                        'E6': 'price_unit${value or 0}#{style=number}',
                        'F6': 'tax_id${value and ","'
                              '.join([x.display_name for x in value]) or ""}',
                        'G6': 'price_subtotal${value or 0}#{style=number}',
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
            # '__POST_IMPORT__': '${object.post_import_do_something()}',
        }
        vals = {
            'res_model': 'sale.order',
            'fname': 'sale_order.xlsx',
            'name': 'Sale Order Template',
            'description': 'Sample Sales Order Tempalte for testing',
            'input_instruction': str(input_instruction),
        }
        cls.sample_template = cls.template_obj.create(vals)

    @classmethod
    def setUpSaleOrder(cls):
        cls.setUpPrepSaleOrder()
        # Create a Sales Order
        product_line = {
            'name': cls.product_order.name,
            'product_id': cls.product_order.id,
            'product_uom_qty': 2,
            'product_uom': cls.product_order.uom_id.id,
            'price_unit': cls.product_order.list_price,
            'tax_id': False,
        }
        cls.sale_order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, product_line), (0, 0, product_line)],
        })

    @classmethod
    def setUpManySaleOrder(cls):
        cls.setUpPrepSaleOrder()
        # Create a Sales Order
        product_line = {
            'name': cls.product_order.name,
            'product_id': cls.product_order.id,
            'product_uom_qty': 2,
            'product_uom': cls.product_order.uom_id.id,
            'price_unit': cls.product_order.list_price,
            'tax_id': False,
        }
        for i in range(10):
            cls.env['sale.order'].create({
                'partner_id': cls.partner.id,
                'order_line': [(0, 0, product_line), (0, 0, product_line)],
            })

    @classmethod
    def setUpPrepSaleOrder(cls):
        categ_ids = cls.env['res.partner.category'].search([]).ids
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test Partner',
            'category_id': [(6, 0, categ_ids)],
        })
        # Create a Product
        user_type_income = \
            cls.env.ref('account.data_account_type_direct_costs')
        cls.account_income_product = cls.env['account.account'].create({
            'code': 'INCOME_PROD111',
            'name': 'Icome - Test Account',
            'user_type_id': user_type_income.id,
        })
        # Create category
        cls.product_category = cls.env['product.category'].create({
            'name': 'Product Category with Income account',
            'property_account_income_categ_id': cls.account_income_product.id
        })
        # Products
        uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.product_order = cls.env['product.product'].create({
            'name': "Test Product",
            'standard_price': 235.0,
            'list_price': 280.0,
            'type': 'consu',
            'uom_id': uom_unit.id,
            'uom_po_id': uom_unit.id,
            'invoice_policy': 'order',
            'expense_policy': 'no',
            'default_code': 'PROD_ORDER',
            'service_type': 'manual',
            'taxes_id': False,
            'categ_id': cls.product_category.id,
        })
