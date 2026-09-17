# Copyright 2016 Akretion Mourad EL HADJ MIMOUNE
# Copyright 2020 Hibou Corp.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from unittest.mock import patch

from odoo import SUPERUSER_ID
from odoo.api import Environment
from odoo.exceptions import UserError, ValidationError
from odoo.orm.model_classes import add_to_registry
from odoo.tests import TransactionCase

from ..exceptions import BaseExceptionError
from .common import (
    mock_base_exception_method_env,
    patch_base_exception_method_env,
    swallow_base_exception_error,
)


class TestBaseException(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, test_base_exception=True))
        cls.originExceptionRuleClasses = cls.registry["exception.rule"]._base_classes__

        from . import purchase_test

        for model_class in [
            purchase_test.ExceptionRule,
            purchase_test.LineTest,
            purchase_test.PurchaseTest,
            purchase_test.WizardTest,
        ]:
            add_to_registry(cls.registry, model_class)

        test_models = [
            "base.exception.test.purchase.line",
            "base.exception.test.purchase",
            "exception.rule.confirm.test.purchase",
        ]
        cls.registry._setup_models__(cls.env.cr, test_models + ["exception.rule"])
        cls.registry.init_models(
            cls.env.cr, test_models + ["exception.rule"], {"models_to_check": True}
        )
        for model_name in test_models:
            cls.addClassCleanup(cls.registry.__delitem__, model_name)
        cls.addClassCleanup(cls.restore_exception_rule)

        cls.partner = cls.env["res.partner"].create({"name": "Foo"})
        cls.po = cls.env["base.exception.test.purchase"].create(
            {
                "name": "Test base exception to basic purchase",
                "partner_id": cls.partner.id,
                "line_ids": [
                    (0, 0, {"name": "line test", "amount": 120.0, "qty": 1.5})
                ],
            }
        )
        cls.exception_rule = cls.env["exception.rule"].create(
            {
                "name": "No ZIP code on destination",
                "sequence": 10,
                "model": "base.exception.test.purchase",
                "code": "if not self.partner_id.zip: failed=True",
                "exception_type": "by_py_code",
            }
        )
        exception_rule_confirm_obj = cls.env["exception.rule.confirm.test.purchase"]
        cls.exception_rule_confirm = exception_rule_confirm_obj.with_context(
            active_model="base.exception.test.purchase", active_ids=cls.po.ids
        ).create(
            {
                "related_model_id": cls.po.id,
                "ignore": False,
            }
        )

    @classmethod
    def restore_exception_rule(cls):
        cls.registry["exception.rule"]._base_classes__ = cls.originExceptionRuleClasses

    @patch_base_exception_method_env
    def test_valid(self):
        self.partner.write({"zip": "00000"})
        self.exception_rule.active = False
        self.po.button_confirm()
        self.assertFalse(self.po.exception_ids)

    def test_exception_rule_confirm(self):
        self.exception_rule_confirm.action_confirm()
        self.assertFalse(self.exception_rule_confirm.exception_ids)

    @patch_base_exception_method_env
    @swallow_base_exception_error
    def test_fail_by_py(self):
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.po.with_context(raise_exception=False).button_confirm()
        self.assertTrue(self.po.exception_ids)

    @patch_base_exception_method_env
    @swallow_base_exception_error
    def test_fail_by_domain(self):
        self.exception_rule.write(
            {
                "domain": "[('partner_id.zip', '=', False)]",
                "exception_type": "by_domain",
            }
        )
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.po.with_context(raise_exception=False).button_confirm()
        self.assertTrue(self.po.exception_ids)

    @patch_base_exception_method_env
    @swallow_base_exception_error
    def test_fail_by_method(self):
        self.exception_rule.write(
            {
                "method": "exception_method_no_zip",
                "exception_type": "by_method",
            }
        )
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.po.with_context(raise_exception=False).button_confirm()
        self.assertTrue(self.po.exception_ids)

    @patch_base_exception_method_env
    @swallow_base_exception_error
    def test_ignorable_exception(self):
        # Block because of exception during validation
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.po.with_context(raise_exception=False).button_confirm()
        # Test that we have linked exceptions
        self.assertTrue(self.po.exception_ids)
        # Test ignore exeception make possible for the po to validate
        self.po.action_ignore_exceptions()
        self.assertTrue(self.po.ignore_exception)
        self.assertFalse(self.po.exceptions_summary)
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")

    def test_purchase_check_exception(self):
        self.po.test_purchase_check_exception()

    def test_purchase_check_button_approve(self):
        self.po.button_approve()
        self.assertEqual(self.po.state, "to approve")

    def test_purchase_check_button_draft(self):
        self.po.button_draft()
        self.assertEqual(self.po.state, "draft")

    @patch_base_exception_method_env
    def test_purchase_check_button_confirm(self):
        self.partner.write({"zip": "00000"})
        self.po.button_confirm()
        self.assertEqual(self.po.state, "purchase")

    def test_purchase_check_button_cancel(self):
        self.po.button_cancel()
        self.assertEqual(self.po.state, "cancel")

    @patch_base_exception_method_env
    @swallow_base_exception_error
    def test_detect_exceptions(self):
        self.po.detect_exceptions()

    @patch_base_exception_method_env
    @swallow_base_exception_error
    def test_blocking_exception(self):
        self.exception_rule.is_blocking = True
        # Block because of exception during validation
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        # Test that we have linked exceptions
        self.po.with_context(raise_exception=False).button_confirm()
        self.assertTrue(self.po.exception_ids)
        self.assertTrue(self.po.exceptions_summary)
        # Test cannot ignore blocked exception
        with self.assertRaises(UserError):
            self.po.action_ignore_exceptions()
        self.assertFalse(self.po.ignore_exception)
        with self.assertRaises(ValidationError):
            self.po.button_confirm()
        self.po.with_context(raise_exception=False).button_confirm()
        self.assertTrue(self.po.exception_ids)
        self.assertTrue(self.po.exceptions_summary)

    def test_rollback_main_transaction(self):
        # Get new TestCursor
        self.registry_enter_test_mode()
        with (
            self.registry.cursor() as new_cr,
            patch(
                "odoo.addons.base_exception.models.base_exception.BaseExceptionModel._check_exception"
            ) as mocked_check_exception,
        ):
            mocked_check_exception.return_value = None
            new_env = Environment(new_cr, SUPERUSER_ID, {"module": "base_exception"})
            with (
                # Use new_env created here instead of the one in base_exception_method
                mock_base_exception_method_env(self, env=new_env),
                self.assertRaises(BaseExceptionError),
            ):
                self.po.button_detect_and_confirm()
            # 1. Entering assertRaises will create a first savepoint using self.env.cr.
            # 2. When write is triggered through new_cr in
            # base.exception.method.detect_exceptions, a second savepoint will be
            # created using new_cr, and an odoo.sql_db.Savepoint object will be stored
            # on new_cr._savepoint for this second savepoint.
            # 3. As the with block of assertRaises is exited a rollback to the first
            # savepoint will be triggered, what invalidates the second savepoint.
            #
            # However, the Savepoint object for the second savepoint will not be
            # removed from new_cr._savepoint, but as both self.env.cr and new_cr
            # use the same psycopg2 cursor object behind the scene, the second
            # savepoint does not exist anymore in the database.
            # This situation would actually trigger a "savepoint does not exist"
            # psycopg2 exception when trying to release or rollback the savepoint
            # when closing the cursor. Therefore, we can safely remove the reference
            # to that object to avoid this error when exiting the test.
            new_cr._savepoint = None
            # Ensure write from base.exception.method.detect_exceptions was called
            #  with the new env that must be committed as the main env is the one to
            #  be rollbacked.
            self.assertFalse(self.po.exception_ids)
            self.assertTrue(self.po.with_env(new_env).exception_ids)
            self.assertNotEqual(self.po.state, "purchase")
            self.assertNotEqual(self.po.with_env(new_env).state, "purchase")
