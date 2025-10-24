# Copyright 2018-19 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright (c) 2022 brain-tec AG (https://braintec.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

from unittest import mock

from lxml import etree

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tests.common import tagged

from ..models.tier_validation import BASE_EXCEPTION_FIELDS as BEF
from ..models.tier_validation import TierValidation as TV
from .common import CommonTierValidation


@tagged("post_install", "-at_install")
class TierTierValidation(CommonTierValidation):
    def test_01_auto_validation(self):
        """When the user can validate all future reviews, it is not needed
        to request a validation, the action can be done straight forward."""
        self.test_record.with_user(self.test_user_1.id).action_confirm()
        self.assertEqual(self.test_record.state, "confirmed")

    def test_02_no_auto_validation(self):
        """User with no right to validate future reviews must request a
        validation."""
        with self.assertRaises(ValidationError):
            self.test_record.with_user(self.test_user_2.id).action_confirm()

    def test_03_request_validation_approved(self):
        """User 2 request a validation and user 1 approves it."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.with_user(self.test_user_1.id)
        record.validate_tier()
        self.assertEqual(record.validation_status, "validated")

    def test_04_request_validation_rejected(self):
        """Request validation, rejection and reset."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.with_user(self.test_user_1.id)
        record.reject_tier()
        self.assertTrue(record.review_ids)
        self.assertEqual(record.validation_status, "rejected")
        record.restart_validation()
        self.assertFalse(record.review_ids)

    def test_05_under_validation(self):
        """Write is forbidden in a record under validation."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.with_user(self.test_user_1.id)
        with self.assertRaises(ValidationError):
            record.write({"test_field": 0.5})

    def test_06_validation_process_open(self):
        """Operation forbidden while a validation process is open."""
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.with_user(self.test_user_1.id)
        with self.assertRaises(ValidationError):
            record.action_confirm()

    def test_07_search_reviewers(self):
        """Test search methods."""
        reviews = self.test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        record = self.test_record.with_user(self.test_user_1.id)
        self.assertIn(self.test_user_1, record.reviewer_ids)
        res = self.test_model.search([("reviewer_ids", "in", self.test_user_1.id)])
        self.assertTrue(res)

    def test_10_systray_counter(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions for both tester models
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model_2.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
            }
        )
        # Request validation
        self.test_record.with_user(self.test_user_2.id).request_validation()
        test_record.with_user(self.test_user_2.id).request_validation()
        self.test_record_2.with_user(self.test_user_2.id).request_validation()
        # Get review user count as systray icon would do and check count value
        docs = self.test_user_1.with_user(self.test_user_1).review_user_count()
        self.assertEqual(
            next(filter(lambda doc: doc["model"] == "tier.validation.tester", docs))[
                "pending_count"
            ],
            2,
        )
        self.assertEqual(
            next(filter(lambda doc: doc["model"] == "tier.validation.tester2", docs))[
                "pending_count"
            ],
            1,
        )

    def test_11_add_comment(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "has_comment": True,
            }
        )
        # Request validation
        review = test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(review)
        # Let _compute_can_review assign status 'pending' instead of waiting
        review.flush_recordset()
        record = test_record.with_user(self.test_user_1.id)
        res = record.validate_tier()
        ctx = res.get("context")
        wizard = Form(self.env["comment.wizard"].with_context(**ctx))
        wizard.comment = "Test Comment"
        wiz = wizard.save()
        wiz.add_comment()
        self.assertTrue(test_record.review_ids.filtered("comment"))
        # Check notify
        comment = test_record.with_user(
            self.test_user_1.id
        )._notify_accepted_reviews_body()
        self.assertEqual(comment, "A review was accepted. (Test Comment)")
        comment = test_record.with_user(
            self.test_user_1.id
        )._notify_rejected_review_body()
        self.assertEqual(comment, "A review was rejected by John. (Test Comment)")

    def test_11_add_comment_rejection(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "has_comment": True,
            }
        )
        # Request validation
        review = test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(review)
        record = test_record.with_user(self.test_user_1.id)
        res = record.reject_tier()  # Rejection
        ctx = res.get("context")
        wizard = Form(self.env["comment.wizard"].with_context(**ctx))
        wizard.comment = "Test Comment"
        wiz = wizard.save()
        wiz.add_comment()
        self.assertTrue(test_record.review_ids.filtered("comment"))
        # Check notify
        comment = test_record.with_user(
            self.test_user_1.id
        )._notify_accepted_reviews_body()
        self.assertEqual(comment, "A review was accepted. (Test Comment)")
        comment = test_record.with_user(
            self.test_user_1.id
        )._notify_rejected_review_body()
        self.assertEqual(comment, "A review was rejected by John. (Test Comment)")

    def test_12_approve_sequence(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "sequence": 30,
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "sequence": 10,
            }
        )
        # Request validation
        self.assertFalse(self.test_record.review_ids)
        reviews = test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)

        docs1 = self.test_user_2.with_user(self.test_user_1).review_user_count()
        for doc in docs1:
            self.assertEqual(doc.get("pending_count"), 1)
        docs2 = self.test_user_2.with_user(self.test_user_2).review_user_count()
        for doc in docs2:
            self.assertEqual(doc.get("pending_count"), 0)

        record1 = test_record.with_user(self.test_user_1.id)
        self.assertTrue(record1.can_review)
        record2 = test_record.with_user(self.test_user_2.id)
        self.assertFalse(record2.can_review)
        # User 1 validates the record, 2 review should be approved.
        self.assertFalse(any(r.status == "approved" for r in record1.review_ids))
        record1.validate_tier()
        self.assertTrue(any(r.status == "approved" for r in record1.review_ids))

    def test_12_approve_sequence_same_user(self):
        """Similar to test_12_approve_sequence, but all same users,
        the approve_sequence still apply correctly"""
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "sequence": 20,
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "sequence": 10,
            }
        )
        # Request validation
        self.assertFalse(self.test_record.review_ids)
        reviews = test_record.with_user(self.test_user_1.id).request_validation()
        self.assertTrue(reviews)

        record1 = test_record.with_user(self.test_user_1.id)
        self.assertTrue(record1.can_review)
        # Validation will be all by sequence
        self.assertEqual(len(record1.review_ids), 2)
        self.assertEqual(
            1, len(record1.review_ids.filtered(lambda x: x.status == "waiting"))
        )
        self.assertEqual(
            1, len(record1.review_ids.filtered(lambda x: x.status == "pending"))
        )
        record1.validate_tier()
        self.assertEqual(
            0, len(record1.review_ids.filtered(lambda x: x.status == "waiting"))
        )
        self.assertEqual(
            1, len(record1.review_ids.filtered(lambda x: x.status == "pending"))
        )
        self.assertEqual(
            1, len(record1.review_ids.filtered(lambda x: x.status == "approved"))
        )
        record1.validate_tier()
        self.assertEqual(
            0, len(record1.review_ids.filtered(lambda x: x.status == "waiting"))
        )
        self.assertEqual(
            0, len(record1.review_ids.filtered(lambda x: x.status == "pending"))
        )
        self.assertEqual(
            2, len(record1.review_ids.filtered(lambda x: x.status == "approved"))
        )
        record1.validate_tier()
        self.assertEqual(
            0, len(record1.review_ids.filtered(lambda x: x.status == "waiting"))
        )
        self.assertEqual(
            0, len(record1.review_ids.filtered(lambda x: x.status == "pending"))
        )
        self.assertEqual(
            2, len(record1.review_ids.filtered(lambda x: x.status == "approved"))
        )

    def test_12_approve_sequence_same_user_bypassed(self):
        """Similar to test_12_approve_sequence, with all same users,
        but approve_sequence_bypass is True"""
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "approve_sequence_bypass": True,
                "sequence": 20,
            }
        )
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
                "approve_sequence_bypass": True,
                "sequence": 10,
            }
        )
        # Request validation
        self.assertFalse(self.test_record.review_ids)
        reviews = test_record.with_user(self.test_user_1.id).request_validation()
        self.assertTrue(reviews)

        record1 = test_record.with_user(self.test_user_1.id)
        self.assertTrue(record1.can_review)
        # When the first tier is validated, all the rest will be approved.
        self.assertEqual(len(record1.review_ids), 2)
        self.assertEqual(
            1, len(record1.review_ids.filtered(lambda x: x.status == "waiting"))
        )
        self.assertEqual(
            1, len(record1.review_ids.filtered(lambda x: x.status == "pending"))
        )
        record1.validate_tier()
        self.assertEqual(
            0, len(record1.review_ids.filtered(lambda x: x.status == "pending"))
        )
        self.assertEqual(
            0, len(record1.review_ids.filtered(lambda x: x.status == "waiting"))
        )
        self.assertEqual(
            2, len(record1.review_ids.filtered(lambda x: x.status == "approved"))
        )

    def test_13_onchange_review_type(self):
        tier_def_id = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
            }
        )
        self.assertTrue(tier_def_id.reviewer_id)
        tier_def_id.review_type = "group"
        tier_def_id.onchange_review_type()
        self.assertFalse(tier_def_id.reviewer_id)

    def test_14_onchange_review_type(self):
        tier_def_id = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
            }
        )
        self.assertTrue(tier_def_id.reviewer_id)
        tier_def_id.review_type = "group"
        tier_def_id.onchange_review_type()
        self.assertFalse(tier_def_id.reviewer_id)

    def test_15_review_user_count(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 2.5})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_1.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "has_comment": True,
            }
        )
        # Request validation
        review = test_record.with_user(self.test_user_2).request_validation()
        self.assertTrue(review)
        self.assertTrue(self.test_user_1.review_ids)
        self.assertTrue(test_record.review_ids)
        # Used by front-end
        count = self.test_user_1.with_user(self.test_user_1).review_user_count()
        self.assertEqual(len(count), 1)
        # False Review - test notification message bodies
        self.assertIn("created", self.test_record._notify_created_review_body())
        self.assertNotEqual(self.test_record.validation_status, "validated")
        self.assertIn("requested", self.test_record._notify_requested_review_body())
        self.assertIn("rejected", self.test_record._notify_rejected_review_body())
        self.assertIn("accepted", self.test_record._notify_accepted_reviews_body())

    def test_16_review_user_count_on_rejected(self):
        """If document is rejected, it should always removed from tray"""
        # Create new test record
        test_record3 = self.test_model.create({"test_field": 1.0})
        # Create tier definitions
        self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "definition_domain": "[('test_field', '=', 1.0)]",
            }
        )
        test_record3.with_user(self.test_user_2).request_validation()
        record1 = test_record3.with_user(self.test_user_1)
        self.assertTrue(record1.can_review)
        self.assertTrue(
            self.test_user_1.with_user(self.test_user_1).review_user_count()
        )
        self.assertTrue(
            self.test_user_2.with_user(self.test_user_2).review_user_count()
        )
        # user 1 reject first tier
        record1.reject_tier()
        self.assertFalse(record1.can_review)
        # both user 1 and 2 has nothing left in tray
        self.assertFalse(
            self.test_user_1.with_user(self.test_user_1).review_user_count()
        )
        self.assertFalse(
            self.test_user_2.with_user(self.test_user_2).review_user_count()
        )

    def test_17_search_records_no_validation(self):
        """Search for records that have no validation process started"""
        records = self.env["tier.validation.tester"].search(
            [("reviewer_ids", "=", False)]
        )
        self.assertEqual(len(records), 1)
        self.test_record.with_user(self.test_user_2.id).request_validation()
        self.test_record.with_user(self.test_user_1.id)
        records = self.env["tier.validation.tester"].search(
            [("reviewer_ids", "=", False)]
        )
        self.assertEqual(len(records), 0)

    def test_18_test_review_by_res_users_field(self):
        selected_field = self.env["ir.model.fields"].search(
            [("model", "=", self.test_model._name), ("name", "=", "user_id")]
        )
        test_record = self.test_model.create(
            {"test_field": 2.5, "user_id": self.test_user_2.id}
        )

        definition = self.env["tier.definition"].create(
            {
                "model_id": self.tester_model.id,
                "review_type": "field",
                "reviewer_field_id": selected_field.id,
                "definition_domain": "[('test_field', '>', 1.0)]",
                "approve_sequence": True,
            }
        )

        reviews = test_record.request_validation()
        review = reviews.filtered(lambda r: r.definition_id == definition)
        self.assertTrue(review)
        self.assertEqual(review.reviewer_ids, self.test_user_2)

    def test_19_waiting_tier(self):
        # Create new test record
        tier_review_obj = self.env["tier.review"]
        test_record = self.test_model.create({"test_field": 3.5})
        # Request validation
        review = test_record.request_validation()

        self.assertTrue(review)
        # both reviews should be waiting when created
        review_1 = tier_review_obj.browse(review.ids[0])
        review_2 = tier_review_obj.browse(review.ids[1])
        self.assertTrue(review_1.status == "waiting")
        self.assertTrue(review_2.status == "waiting")
        # and then normal workflow will follow...
        review_1.invalidate_model()
        review_1._compute_can_review()
        self.assertTrue(review_1.status == "pending")
        # first reviewer does not want notifications
        # chatter should be empty
        self.assertFalse(test_record.message_ids)
        self.assertTrue(review_1.done_by.id is False)
        self.assertTrue(review_1.reviewed_date is False)
        self.assertTrue(review_2.status == "waiting")
        self.assertTrue(review_2.done_by.id is False)
        self.assertTrue(review_2.reviewed_date is False)
        record = test_record.with_user(self.test_user_1.id)
        record.invalidate_model()
        record.validate_tier()
        self.assertTrue(review_1.status == "approved")
        self.assertFalse(review_1.reviewed_date is False)
        self.assertTrue(review_1.done_by.id == self.test_user_1.id)
        self.assertTrue(review_2.status == "pending")
        self.assertTrue(review_2.done_by.id is False)
        self.assertTrue(review_2.reviewed_date is False)

    def test_20_no_sequence(self):
        # Create new test record
        tier_review_obj = self.env["tier.review"]
        test_record2 = self.test_model.create({"test_field": 0.9})
        # request validation
        review = test_record2.request_validation()
        self.assertTrue(review)
        review_1 = tier_review_obj.browse(review.ids[0])
        self.assertTrue(review_1.status == "waiting")
        review_1.invalidate_model()
        review_1._compute_can_review()
        self.assertTrue(review_1.status == "pending")
        msg2 = test_record2.message_ids[0].body
        request = test_record2._notify_requested_review_body()
        self.assertIn(request, msg2)

    def test_21_notify_on_create(self):
        # notify on create
        tier_definition = self.env["tier.definition"].search([])
        tier_definition.write(
            {
                "notify_on_create": True,
                "notify_on_accepted": False,
                "notify_on_rejected": False,
                "notify_on_restarted": False,
                "review_type": "group",
                "reviewer_group_id": self.env.ref("base.group_system").id,
            }
        )
        test_record_1 = self.test_model.create({"test_field": 1})
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        test_record_1.request_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

        # do not notify on create
        tier_definition.write({"notify_on_create": False})
        test_record_2 = self.test_model.create({"test_field": 1})
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        test_record_2.request_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

    def test_22_notify_on_accepted(self):
        self.test_user_2.write(
            {
                "group_ids": [(6, 0, self.env.ref("base.group_system").ids)],
            }
        )

        # notify on accepted
        tier_definition = self.env["tier.definition"].search([])
        tier_definition.write(
            {
                "notify_on_create": False,
                "notify_on_accepted": True,
                "notify_on_rejected": False,
                "notify_on_restarted": False,
                "review_type": "group",
                "reviewer_group_id": self.env.ref("base.group_system").id,
            }
        )
        test_record_1 = self.test_model.create({"test_field": 1})
        test_record_1.request_validation()
        record = test_record_1.with_user(self.test_user_2.id)
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.validate_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

        # do not notify on accepted
        tier_definition.write({"notify_on_accepted": False})
        test_record_2 = self.test_model.create({"test_field": 1})
        test_record_2.request_validation()
        test_record_2.with_user(self.test_user_2.id)
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        test_record_2.validate_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

    def test_23_notify_on_rejected(self):
        self.test_user_2.write(
            {
                "group_ids": [(6, 0, self.env.ref("base.group_system").ids)],
            }
        )

        # notify on rejected
        tier_definition = self.env["tier.definition"].search([])
        tier_definition.write(
            {
                "notify_on_create": False,
                "notify_on_accepted": False,
                "notify_on_rejected": True,
                "notify_on_restarted": False,
                "review_type": "group",
                "reviewer_group_id": self.env.ref("base.group_system").id,
            }
        )
        test_record_1 = self.test_model.create({"test_field": 1})
        test_record_1.request_validation()
        record = test_record_1.with_user(self.test_user_2.id)
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.reject_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

        # do not notify on rejected
        tier_definition.write({"notify_on_rejected": False})
        test_record_2 = self.test_model.create({"test_field": 1})
        test_record_2.request_validation()
        test_record_2.with_user(self.test_user_2.id)

        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        test_record_2.reject_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

    def test_24_notify_on_restarted(self):
        self.test_user_2.write(
            {
                "group_ids": [(6, 0, self.env.ref("base.group_system").ids)],
            }
        )

        # notify on restarted
        tier_definition = self.env["tier.definition"].search([])
        tier_definition.write(
            {
                "notify_on_create": False,
                "notify_on_accepted": False,
                "notify_on_rejected": False,
                "notify_on_restarted": True,
                "review_type": "group",
                "reviewer_group_id": self.env.ref("base.group_system").id,
            }
        )
        test_record_1 = self.test_model.create({"test_field": 1})
        test_record_1.request_validation()
        record = test_record_1.with_user(self.test_user_2.id)
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.restart_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

        # do not notify on restarted
        tier_definition.write({"notify_on_restarted": False})
        test_record_2 = self.test_model.create({"test_field": 1})
        test_record_2.request_validation()
        test_record_2.with_user(self.test_user_2.id)
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        test_record_2.restart_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

    def test_25_all_notification(self):
        self.test_user_2.write(
            {
                "group_ids": [(6, 0, self.env.ref("base.group_system").ids)],
            }
        )

        # notify on restarted
        tier_definition = self.env["tier.definition"].search([])
        tier_definition.write(
            {
                "notify_on_create": True,
                "notify_on_accepted": True,
                "notify_on_rejected": True,
                "notify_on_restarted": True,
                "review_type": "group",
                "reviewer_group_id": self.env.ref("base.group_system").id,
            }
        )

        test_record = self.test_model.create({"test_field": 1})

        # request validation
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        test_record.request_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

        # accept validation
        record = test_record.with_user(self.test_user_2.id)
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.validate_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

        # restart validation
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.restart_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

        # reject validation
        record.request_validation()
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.reject_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1 + 1)

    def test_26_no_notification(self):
        self.test_user_2.write(
            {
                "group_ids": [(6, 0, self.env.ref("base.group_system").ids)],
            }
        )

        # notify on restarted
        tier_definition = self.env["tier.definition"].search([])
        tier_definition.write(
            {
                "notify_on_create": False,
                "notify_on_accepted": False,
                "notify_on_rejected": False,
                "notify_on_restarted": False,
                "review_type": "group",
                "reviewer_group_id": self.env.ref("base.group_system").id,
            }
        )

        test_record = self.test_model.create({"test_field": 1})

        # request validation
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        test_record.request_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

        # accept validation
        record = test_record.with_user(self.test_user_2.id)
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.validate_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

        # restart validation
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.restart_validation()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

        # reject validation
        record.request_validation()
        notifications_no_1 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        record.reject_tier()
        notifications_no_2 = len(
            self.env["mail.notification"].search(
                [("res_partner_id", "=", self.test_user_1.partner_id.id)]
            )
        )
        self.assertEqual(notifications_no_2, notifications_no_1)

    def test_27_change_field_exception_validation(self):
        """Test under and after validations"""
        # Cannot create `tier.validation.exception` records because
        # `tier.validation.tester` are fake model and its fields are
        # not propagated to the DDBB and cannot read from `ir.model.fields`.
        # We will use the mock.patch instead.
        _tvf = ["test_validation_field"]
        _rv = _tvf + BEF
        self.assertEqual(self.test_record.test_validation_field, 0)
        self.assertFalse(self.test_record.review_ids)
        reviews = self.test_record.with_user(self.test_user_2.id).request_validation()
        self.assertTrue(reviews)
        self.assertTrue(self.test_record.review_ids)
        # Unable to write test_validation_field under validation
        with self.assertRaises(ValidationError):
            self.test_record.with_user(self.test_user_2.id).write(
                {"test_validation_field": 1}
            )
        # Able to write test_validation_field under validation
        with mock.patch.object(
            TV, "_get_under_validation_exceptions", return_value=_rv
        ):
            self.test_record.with_user(self.test_user_2.id).write(
                {"test_validation_field": 2}
            )
        self.assertEqual(self.test_record.test_validation_field, 2)
        # Validate record
        record = self.test_record.with_user(self.test_user_1.id)
        record.validate_tier()
        record.action_confirm()
        self.assertEqual(record.validation_status, "validated")
        # Unable to write test_validation_field after validation
        with self.assertRaises(ValidationError):
            # Simulate there are fields, but not test_validation_field
            with mock.patch.object(TV, "_get_validation_exceptions", return_value=BEF):
                self.test_record.with_user(self.test_user_2.id).write(
                    {"test_validation_field": 3}
                )
        # Able to write test_validation_field after validation
        with mock.patch.multiple(
            TV,
            _get_validation_exceptions=mock.MagicMock(return_value=_tvf),
            _get_after_validation_exceptions=mock.MagicMock(return_value=_rv),
        ):
            self.test_record.with_user(self.test_user_2.id).write(
                {"test_validation_field": 4}
            )
        self.assertEqual(self.test_record.test_validation_field, 4)

    def test_28_computed_state_field(self):
        """Test the regular flow on a model where state is a computed field"""
        # The record cannot be confirmed without validation
        with self.assertRaisesRegex(
            ValidationError,
            "This action needs to be validated",
        ):
            with self.env.cr.savepoint():
                self.test_record_computed.action_confirm()
                # Flush manually to trigger the _write
                self.test_record_computed.flush_recordset()
        self.assertEqual(self.test_record_computed.state, "draft")
        # The validation is performed
        self.test_record_computed.request_validation()
        self.test_record_computed.invalidate_recordset()
        self.assertEqual(self.test_record_computed.review_ids.status, "waiting")
        self.test_record_computed.with_user(self.test_user_1).validate_tier()
        self.test_record_computed.invalidate_recordset()
        self.assertEqual(self.test_record_computed.review_ids.status, "approved")
        # After validation, the record can be confirmed
        self.test_record_computed.action_confirm()
        self.test_record_computed.flush_recordset()
        self.assertEqual(self.test_record_computed.state, "confirmed")
        # After cancelling, the reviews are removed
        self.test_record_computed.action_cancel()
        self.test_record_computed.flush_recordset()
        self.assertFalse(self.test_record_computed.review_ids)
        self.test_record_computed.invalidate_recordset()

    def test_29_allow_write_for_reviewers(self):
        reviews = self.test_record.with_user(self.test_user_2.id).request_validation()
        record = self.test_record.with_user(self.test_user_1.id)
        record.invalidate_recordset()
        with self.assertRaises(ValidationError):
            record.with_user(self.test_user_1.id).write({"test_field": 0.3})
        reviews.definition_id.with_user(self.test_user_1.id).write(
            {"allow_write_for_reviewer": True}
        )
        record.with_user(self.test_user_1.id).write({"test_field": 0.3})

    def test_30_request_validation_diff_company(self):
        """
        Test validation request behavior with multi-company setup.

        Setup:
        - Main company has 2 tier definitions:
          - One for User1 (sequence 30)
          - One for User3 (sequence 20)
        - Other company has 1 tier definition:
          - One for User3 (sequence 30)

        When record's company is set to 'other company':
        - Only User3's tier definition from other company should be applied
        - Should create only 1 review
        """
        self.assertFalse(self.test_record_2.review_ids)
        self.assertFalse(self.test_record_2.company_id)
        self.assertEqual(self.test_user_3_multi_company.env.company, self.main_company)

        self.test_record_2.company_id = self.other_company

        reviews = self.test_record_2.with_user(
            self.test_user_3_multi_company.id
        ).request_validation()

        self.assertEqual(len(reviews), 1)

    def test_31_request_validation_same_company(self):
        """
        Test validation request behavior with multi-company setup.

        Setup:
        - Main company has 2 tier definitions:
          - One for User1 (sequence 30)
          - One for User3 (sequence 20)
        - Other company has 1 tier definition:
          - One for User3 (sequence 30)

        When record's company is set to 'main company':
        - Both User1 and User3's tier definitions from main company should be applied
        - Should create 2 reviews
        """
        self.assertFalse(self.test_record_2.review_ids)
        self.assertFalse(self.test_record_2.company_id)
        self.assertEqual(self.test_user_3_multi_company.env.company, self.main_company)

        self.test_record_2.company_id = self.main_company

        reviews = self.test_record_2.with_user(
            self.test_user_3_multi_company.id
        ).request_validation()

        self.assertEqual(len(reviews), 2)

    def test_30_request_validation(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 1.0})
        # Create tier definitions for both tester models
        self.tier_definition.write(
            {
                "approve_sequence": True,
                "notify_on_create": True,
            }
        )
        def_2 = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "sequence": 20,
                "approve_sequence": True,
                "notify_on_create": False,
                "notify_on_accepted": True,
            }
        )
        def_3 = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_3_multi_company.id,
                "sequence": 10,
                "approve_sequence": True,
                "notify_on_create": False,
                "notify_on_accepted": True,
            }
        )
        mt_tier_validation_requested = self.env.ref(
            "base_tier_validation.mt_tier_validation_requested"
        )
        mt_tier_validation_accepted = self.env.ref(
            "base_tier_validation.mt_tier_validation_accepted"
        )
        test_record.request_validation()
        review_1 = test_record.review_ids.filtered(
            lambda x: x.definition_id == self.tier_definition
        )
        self.assertEqual(review_1.status, "pending")
        review_2 = test_record.review_ids.filtered(lambda x: x.definition_id == def_2)
        self.assertEqual(review_2.status, "waiting")
        review_3 = test_record.review_ids.filtered(lambda x: x.definition_id == def_3)
        self.assertEqual(review_3.status, "waiting")
        followers = test_record.message_follower_ids
        self.assertIn(self.test_user_1.partner_id, followers.mapped("partner_id"))
        follower_1 = followers.filtered(
            lambda x: x.partner_id == self.test_user_1.partner_id
        )
        self.assertIn(mt_tier_validation_requested, follower_1.subtype_ids)
        self.assertNotIn(mt_tier_validation_accepted, follower_1.subtype_ids)
        self.assertNotIn(self.test_user_2.partner_id, followers.mapped("partner_id"))
        self.assertNotIn(
            self.test_user_3_multi_company.partner_id, followers.mapped("partner_id")
        )
        old_messages = test_record.message_ids
        test_record.with_user(self.test_user_1).validate_tier()
        new_messages = test_record.message_ids - old_messages
        self.assertEqual(len(new_messages), 1)
        self.assertEqual(new_messages.subtype_id, mt_tier_validation_accepted)
        self.assertEqual(self.test_user_2.partner_id, new_messages.notified_partner_ids)
        self.assertEqual(review_1.status, "approved")
        self.assertEqual(review_2.status, "pending")
        self.assertEqual(review_3.status, "waiting")
        followers = test_record.message_follower_ids
        self.assertIn(self.test_user_1.partner_id, followers.mapped("partner_id"))
        self.assertIn(self.test_user_2.partner_id, followers.mapped("partner_id"))
        follower_2 = followers.filtered(
            lambda x: x.partner_id == self.test_user_2.partner_id
        )
        self.assertNotIn(mt_tier_validation_requested, follower_2.subtype_ids)
        self.assertIn(mt_tier_validation_accepted, follower_2.subtype_ids)
        self.assertNotIn(
            self.test_user_3_multi_company.partner_id, followers.mapped("partner_id")
        )
        old_messages = test_record.message_ids
        test_record.with_user(self.test_user_2).validate_tier()
        new_messages = test_record.message_ids - old_messages
        self.assertEqual(len(new_messages), 1)
        self.assertEqual(new_messages.subtype_id, mt_tier_validation_accepted)
        self.assertEqual(
            self.test_user_3_multi_company.partner_id, new_messages.notified_partner_ids
        )
        self.assertEqual(review_1.status, "approved")
        self.assertEqual(review_2.status, "approved")
        self.assertEqual(review_3.status, "pending")
        followers = test_record.message_follower_ids
        self.assertIn(self.test_user_1.partner_id, followers.mapped("partner_id"))
        self.assertIn(self.test_user_2.partner_id, followers.mapped("partner_id"))
        self.assertIn(
            self.test_user_3_multi_company.partner_id, followers.mapped("partner_id")
        )
        follower_3 = followers.filtered(
            lambda x: x.partner_id == self.test_user_3_multi_company.partner_id
        )
        self.assertNotIn(mt_tier_validation_requested, follower_3.subtype_ids)
        self.assertIn(mt_tier_validation_accepted, follower_3.subtype_ids)
        old_messages = test_record.message_ids
        test_record.with_user(self.test_user_3_multi_company).validate_tier()
        new_messages = test_record.message_ids - old_messages
        self.assertEqual(len(new_messages), 0)

    def test_31_request_validation(self):
        # Create new test record
        test_record = self.test_model.create({"test_field": 1.0})
        # Create tier definitions for both tester models
        self.tier_definition.write(
            {
                "approve_sequence": True,
                "notify_on_create": True,
            }
        )
        def_2 = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_2.id,
                "sequence": 20,
                "approve_sequence": True,
                "notify_on_create": True,
                "notify_on_accepted": True,
            }
        )
        def_3 = self.tier_def_obj.create(
            {
                "model_id": self.tester_model.id,
                "review_type": "individual",
                "reviewer_id": self.test_user_3_multi_company.id,
                "sequence": 10,
                "approve_sequence": True,
                "notify_on_create": True,
                "notify_on_accepted": True,
            }
        )
        test_record.request_validation()
        review_1 = test_record.review_ids.filtered(
            lambda x: x.definition_id == self.tier_definition
        )
        self.assertEqual(review_1.status, "pending")
        review_2 = test_record.review_ids.filtered(lambda x: x.definition_id == def_2)
        self.assertEqual(review_2.status, "waiting")
        review_3 = test_record.review_ids.filtered(lambda x: x.definition_id == def_3)
        self.assertEqual(review_3.status, "waiting")
        followers = test_record.message_follower_ids
        self.assertIn(self.test_user_1.partner_id, followers.mapped("partner_id"))
        self.assertIn(self.test_user_2.partner_id, followers.mapped("partner_id"))
        self.assertIn(
            self.test_user_3_multi_company.partner_id, followers.mapped("partner_id")
        )


@tagged("at_install")
class TierTierValidationView(CommonTierValidation):
    def test_view_manual(self):
        view = self.env[self.test_record._name].get_view(False, "form")
        with Form(self.test_record) as f:
            self.assertNotIn("review_ids", f._values)
            form = etree.fromstring(view["arch"])
            self.assertFalse(form.xpath("//field[@name='review_ids']"))
            self.assertFalse(form.xpath("//field[@name='can_review']"))
            self.assertFalse(form.xpath("//button[@name='request_validation']"))

    def test_view_automatic(self):
        view = self.env[self.test_record_2._name].get_view(False, "form")
        with Form(self.test_record_2) as f:
            self.assertIn("review_ids", f._values)
            form = etree.fromstring(view["arch"])
            self.assertTrue(form.xpath("//field[@name='review_ids']"))
            self.assertTrue(form.xpath("//field[@name='can_review']"))
            self.assertTrue(form.xpath("//button[@name='request_validation']"))

    def test_get_view(self):
        view = self.test_record_2.get_view()
        model = "tier.validation.tester2"
        self.assertEqual(view["model"], model)
        self.assertEqual(view["models"].keys(), {model, "tier.review"})
        self.assertIn("id", view["models"][model])
        self.assertIn("need_validation", view["models"][model])
        self.assertIn("next_review", view["models"][model])
        self.assertIn("review_ids", view["models"][model])
