from odoo import fields
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.addons.auditlog.tests.common import AuditLogRuleCommon


@tagged("post_install", "-at_install")
class TestProductTaxMulticompany(AccountTestInvoicingCommon, AuditLogRuleCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company1 = cls.company_data["company"]
        cls.tax1 = cls.company_data["default_tax_sale"]
        cls.company_data_2 = cls.setup_other_company()
        cls.company2 = cls.company_data_2["company"]
        cls.tax2 = cls.company_data_2["default_tax_sale"]
        cls.product_a.sudo().taxes_id = cls.tax1 + cls.tax2
        cls.env.user.company_ids = cls.company1

    def setUp(self):
        super().setUp()
        rules = self.env["auditlog.rule"].search([])
        rules.unsubscribe()
        rules.unlink()
        self.rule = self.env["auditlog.rule"].create(
            {
                "name": __name__,
                "model_id": self.env.ref("product.model_product_template").id,
                "log_read": True,
                "log_create": True,
                "log_write": True,
                "log_unlink": True,
                "log_type": "full",
            }
        )
        self.rule.subscribe()

    def test_cache_accesserror(self):
        """No AccessError occurs reading the product after writing taxes.

        The current user only has access to one of the taxes assigned to the
        product. If auditlog does sanitize the cache after fetching old and
        new values for the log lines, the other company's tax may remain in the
        product's cache which will raise an AccessError when it is read.
        """
        product = self.product_a.product_tmpl_id
        product.write(
            {"taxes_id": [fields.Command.unlink(self.tax1.id)]},
        )
        self.tax1.invalidate_model()
        product.read(["taxes_id"])

    def test_product_tax_multicompany_result(self):
        """The value from the other company is preserved"""
        product = self.product_a.product_tmpl_id
        product.write(
            {"taxes_id": [fields.Command.unlink(self.tax1.id)]},
        )
        self.assertFalse(product.taxes_id)
        product.invalidate_recordset()
        self.assertEqual(product.sudo().taxes_id, self.tax2)

    def test_product_tax_multicompany_log(self):
        """The log covers the taxes across all companies."""
        product = self.product_a.product_tmpl_id
        product.write(
            {"taxes_id": [fields.Command.unlink(self.tax1.id)]},
        )
        log = self.env["auditlog.log"].search([], order="id desc", limit=1)
        self.assertEqual(log.line_ids.old_value, f"[{self.tax1.id}, {self.tax2.id}]")
        self.assertEqual(log.line_ids.new_value, f"[{self.tax2.id}]")
