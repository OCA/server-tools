# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.exceptions import ValidationError
from odoo.tests import common, new_test_user
from odoo.tests.common import tagged

from .common import setup_test_model, teardown_test_model
from .tier_validation_tester import TierValidationTester


@tagged("post_install", "-at_install")
class TestBaseChangesetTierValidation(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Remove this variable in v16 and put instead:
        # from odoo.addons.base.tests.common import DISABLED_MAIL_CONTEXT
        DISABLED_MAIL_CONTEXT = {
            "tracking_disable": True,
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.env = cls.env(context=dict(cls.env.context, **DISABLED_MAIL_CONTEXT))
        setup_test_model(cls.env, [TierValidationTester])
        cls.test_model = cls.env[TierValidationTester._name]
        cls.tester_model = cls.env["ir.model"].search(
            [("model", "=", "tier.validation.tester")]
        )
        user_id_field = cls.tester_model.field_id.filtered(
            lambda x: x.name == "user_id"
        )
        cls.env["changeset.field.rule"].create(
            {
                "field_id": user_id_field.id,
                "action": "validate",
            }
        )
        # Access record:
        cls.env["ir.model.access"].create(
            {
                "name": "access.tester",
                "model_id": cls.tester_model.id,
                "perm_read": 1,
                "perm_write": 1,
                "perm_create": 1,
                "perm_unlink": 1,
            }
        )
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            groups="base.group_user",
        )
        cls.manager = new_test_user(
            cls.env,
            login="test-manager",
            groups="%s,%s,%s"
            % (
                "base.group_user",
                "base_changeset.group_changeset_user",
                "base_changeset.group_changeset_manager",
            ),
        )
        cls.env["changeset.field.rule"].search(
            [("model_id", "=", cls.tester_model.id)]
        ).unlink()
        cls.tier_definition = cls.env["tier.definition"].create(
            {
                "name": "Test tier.validation.tester",
                "model_id": cls.tester_model.id,
                "summary_field_id": cls.tester_model.field_id.filtered(
                    lambda x: x.name == "test_field"
                ).id,
                "review_type": "individual",
                "reviewer_id": cls.manager.id,
                "definition_type": "domain",
            }
        )
        cls.env["changeset.field.rule"].create(
            {
                "model_id": cls.tester_model.id,
                "field_id": cls.tester_model.field_id.filtered(
                    lambda x: x.name == "test_field"
                ).id,
                "create_tier_review": True,
                "tier_definition_id": cls.tier_definition.id,
                "action": "validate",
            }
        )
        cls.env["changeset.field.rule"].create(
            {
                "model_id": cls.tester_model.id,
                "field_id": cls.tester_model.field_id.filtered(
                    lambda x: x.name == "user_id"
                ).id,
                "create_tier_review": True,
                "tier_definition_id": cls.tier_definition.id,
                "action": "validate",
            }
        )
        cls.env = cls.env(context=dict(cls.env.context, test_record_changeset=True))
        cls.test_record = cls.env[cls.test_model._name].create({})

    @classmethod
    def tearDownClass(cls):
        teardown_test_model(cls.env, [TierValidationTester])
        return super().tearDownClass()

    def test_update_tier_validation_tester_simple_validate(self):
        test_record_user = self.test_record.with_user(self.user)
        test_record_manager = self.test_record.with_user(self.manager)
        test_record_user.write({"test_field": 1.0})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.test_field, 0)
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        self.assertTrue(
            ": +1.0" in test_record_manager.review_ids.summary
        )  # Test Field: +1.0
        self.assertEqual(test_record_manager.changeset_ids.state, "draft")
        self.assertEqual(test_record_manager.changeset_ids.review_ids.status, "pending")
        test_record_manager.review_ids.validate_tier()
        self.assertEqual(test_record_manager.changeset_ids.state, "done")
        self.assertEqual(
            test_record_manager.changeset_ids.review_ids.status, "approved"
        )
        self.assertEqual(test_record_manager.test_field, 1)

    def test_update_tier_validation_tester_simple_reject(self):
        test_record_user = self.test_record.with_user(self.user)
        test_record_manager = self.test_record.with_user(self.manager)
        test_record_user.write({"test_field": 1.0})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.test_field, 0)
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        self.assertTrue(
            ": +1.0" in test_record_manager.review_ids.summary
        )  # Test Field: +1.0
        self.assertEqual(test_record_manager.changeset_ids.state, "draft")
        self.assertEqual(test_record_manager.changeset_ids.review_ids.status, "pending")
        test_record_manager.review_ids.reject_tier()
        self.assertEqual(test_record_manager.changeset_ids.state, "done")
        self.assertEqual(
            test_record_manager.changeset_ids.review_ids.status, "rejected"
        )
        self.assertEqual(test_record_manager.test_field, 0)

    def test_update_tier_validation_tester_full(self):
        test_record_user = self.test_record.with_user(self.user)
        test_record_manager = self.test_record.with_user(self.manager)
        # Change test_field
        test_record_user.write({"test_field": 1.0})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.test_field, 0)
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        self.assertTrue(
            ": +1.0" in test_record_manager.review_ids.summary
        )  # Test Field: +1.0
        # Change user_id
        test_record_user.write({"user_id": self.user.id})
        test_record_manager.invalidate_cache()
        self.assertFalse(test_record_manager.user_id)
        self.assertEqual(test_record_manager.total_pending_reviews, 2)
        # validate first review
        test_record_manager._validate_tier()
        self.assertEqual(test_record_manager.test_field, 1)
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        # validate last review
        test_record_manager._validate_tier()
        self.assertEqual(test_record_manager.user_id, self.user)
        self.assertEqual(test_record_manager.total_pending_reviews, 0)
        # Change user_id
        test_record_user.write({"user_id": self.manager.id})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.user_id, self.user)
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        # reject new review
        test_record_manager._rejected_tier()
        self.assertEqual(test_record_manager.user_id, self.user)
        self.assertEqual(test_record_manager.total_pending_reviews, 0)
        # Change user_id with manager user
        test_record_manager.write({"user_id": self.manager.id})
        self.assertEqual(test_record_manager.user_id, self.manager)
        self.assertEqual(test_record_manager.total_pending_reviews, 0)

    def test_update_tier_validation_tester_state_change(self):
        test_record_user = self.test_record.with_user(self.user)
        test_record_manager = self.test_record.with_user(self.manager)
        # Change test_field
        test_record_user.write({"test_field": 1.0})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.test_field, 0)
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        # Change state to sent
        test_record_manager.write({"state": "sent"})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        # Change state to done
        with self.assertRaises(ValidationError):
            test_record_manager.write({"state": "done"})

    def test_update_tier_validation_tester_changeset_01(self):
        test_record_user = self.test_record.with_user(self.user)
        test_record_manager = self.test_record.with_user(self.manager)
        # Change test_field
        test_record_user.write({"test_field": 1.0})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        self.assertEqual(test_record_manager.changeset_ids.state, "draft")
        self.assertEqual(test_record_manager.changeset_ids.review_ids.status, "pending")
        test_record_manager.changeset_ids.apply()
        self.assertEqual(test_record_manager.changeset_ids.state, "done")
        self.assertEqual(
            test_record_manager.changeset_ids.review_ids.status, "approved"
        )
        self.assertEqual(test_record_manager.test_field, 1)

    def test_update_tier_validation_tester_changeset_02(self):
        test_record_user = self.test_record.with_user(self.user)
        test_record_manager = self.test_record.with_user(self.manager)
        # Change test_field
        test_record_user.write({"test_field": 1.0})
        test_record_manager.invalidate_cache()
        self.assertEqual(test_record_manager.total_pending_reviews, 1)
        self.assertEqual(test_record_manager.changeset_ids.state, "draft")
        self.assertEqual(test_record_manager.changeset_ids.review_ids.status, "pending")
        test_record_manager.changeset_ids.cancel()
        self.assertEqual(test_record_manager.changeset_ids.state, "done")
        self.assertEqual(
            test_record_manager.changeset_ids.review_ids.status, "rejected"
        )
        self.assertEqual(test_record_manager.test_field, 0)
