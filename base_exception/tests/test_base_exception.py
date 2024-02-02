# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo_test_helper import FakeModelLoader

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import common

_logger = logging.getLogger(__name__)


class TestBaseException(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        cls.addClassCleanup(cls.loader.restore_registry)

        # Must be lazy-imported
        from ._purchase_test_models import PurchaseTest, LineTest, ExceptionRule

        cls.loader.update_registry((PurchaseTest, LineTest, ExceptionRule))

        cls.base_exception = cls.env["base.exception"]
        cls.exception_rule = cls.env["exception.rule"]
        if "test_purchase_ids" not in cls.exception_rule._fields:
            field = fields.Many2many("base.exception.test.purchase")
            cls.exception_rule._add_field("test_purchase_ids", field)
        cls.exception_confirm = cls.env["exception.rule.confirm"]
        cls.exception_rule._fields["model"].selection.append(
            ("base.exception.test.purchase", "Purchase Order")
        )

        cls.exception_rule._fields["model"].selection.append(
            ("base.exception.test.purchase.line", "Purchase Order Line")
        )

        cls.partner = cls.env.ref("base.res_partner_1")
        cls.partner.zip = False
        cls.potest1 = cls.env["base.exception.test.purchase"].create(
            {
                "name": "Test base exception to basic purchase",
                "partner_id": cls.partner.id,
                "line_ids": [
                    (0, 0, {"name": "line test", "amount": 120.0, "qty": 1.5})
                ],
            }
        )

    def test_valid(self):
        self.potest1.button_confirm()
        self.assertFalse(self.potest1.exception_ids)

    def test_fail_by_py(self):
        self.exception_amount_total = self.env["exception.rule"].create(
            {
                "name": "Min order except",
                "sequence": 10,
                "model": "base.exception.test.purchase",
                "code": "if obj.amount_total <= 200.0: failed=True",
                "exception_type": "by_py_code",
            }
        )
        with self.assertRaises(ValidationError):
            self.potest1.button_confirm()
        self.assertTrue(self.potest1.exception_ids)

    def test_fail_by_domain(self):
        self.exception_partner_no_zip = self.env["exception.rule"].create(
            {
                "name": "No ZIP code on destination",
                "sequence": 10,
                "model": "base.exception.test.purchase",
                "domain": "[('partner_id.zip', '=', False)]",
                "exception_type": "by_domain",
            }
        )
        with self.assertRaises(ValidationError):
            self.potest1.button_confirm()
        self.assertTrue(self.potest1.exception_ids)

    def test_fail_by_method(self):
        self.exception_no_name = self.env["exception.rule"].create(
            {
                "name": "No name",
                "sequence": 10,
                "model": "base.exception.test.purchase",
                "method": "exception_method_no_zip",
                "exception_type": "by_method",
            }
        )
        with self.assertRaises(ValidationError):
            self.potest1.button_confirm()
        self.assertTrue(self.potest1.exception_ids)

    def test_ignore_exception(self):
        # same as 1st test
        self.exception_amount_total = self.env["exception.rule"].create(
            {
                "name": "Min order except",
                "sequence": 10,
                "model": "base.exception.test.purchase",
                "code": "if obj.amount_total <= 200.0: failed=True",
                "exception_type": "by_py_code",
            }
        )
        # Block because of exception during validation
        with self.assertRaises(ValidationError):
            self.potest1.button_confirm()
        # Test that we have linked exceptions
        self.assertTrue(self.potest1.exception_ids)
        # Test ignore exeception make possible for the po to validate
        self.potest1.action_ignore_exceptions()
        self.potest1.button_confirm()
        self.assertTrue(self.potest1.state == "purchase")
