# Copyright 2017-19 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

import pytz

from odoo import api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class TierReview(models.Model):
    _name = "tier.review"
    _description = "Tier Review"

    name = fields.Char(related="definition_id.name")
    status = fields.Selection(
        [
            ("waiting", "Waiting"),
            ("pending", "Pending"),
            ("rejected", "Rejected"),
            ("approved", "Approved"),
        ],
        default="waiting",
    )
    model = fields.Char(string="Related Document Model", index=True)
    res_id = fields.Many2oneReference(
        string="Related Document ID",
        index=True,
        model_field="model",
    )
    definition_id = fields.Many2one(comodel_name="tier.definition")
    company_id = fields.Many2one(
        related="definition_id.company_id",
        store=True,
    )
    review_type = fields.Selection(related="definition_id.review_type")
    reviewer_id = fields.Many2one(related="definition_id.reviewer_id")
    reviewer_group_id = fields.Many2one(related="definition_id.reviewer_group_id")
    reviewer_field_id = fields.Many2one(related="definition_id.reviewer_field_id")
    reviewer_ids = fields.Many2many(
        string="Reviewers",
        comodel_name="res.users",
        compute="_compute_reviewer_ids",
        store=True,
    )
    display_status = fields.Char(compute="_compute_display_status")
    sequence = fields.Integer(string="Tier")
    todo_by = fields.Char(compute="_compute_todo_by", store=True)
    done_by = fields.Many2one(comodel_name="res.users")
    requested_by = fields.Many2one(comodel_name="res.users")
    reviewed_date = fields.Datetime(string="Validation Date")
    reviewed_formated_date = fields.Char(
        string="Validation Formated Date", compute="_compute_reviewed_formated_date"
    )
    has_comment = fields.Boolean(related="definition_id.has_comment")
    comment = fields.Char(string="Comments")
    can_review = fields.Boolean(
        compute="_compute_can_review",
        store=True,
        help="""Can review will be marked if the review is pending and the
        approve sequence has been achieved""",
    )
    approve_sequence = fields.Boolean(related="definition_id.approve_sequence")
    approve_sequence_bypass = fields.Boolean(
        related="definition_id.approve_sequence_bypass"
    )
    last_reminder_date = fields.Datetime(readonly=True)

    requested_by_name = fields.Char(compute="_compute_user_names", store=True)
    done_by_name = fields.Char(compute="_compute_user_names", store=True)

    @api.depends("status")
    def _compute_display_status(self):
        """
        Compute the display status based on the current status value to get the
        translated status value.
        """
        selection = self.fields_get(["status"])["status"]["selection"]
        selection_dict = dict(selection)
        for record in self:
            record.display_status = selection_dict[record.status]

    @api.depends("requested_by", "done_by")
    def _compute_user_names(self):
        for record in self:
            record.requested_by_name = (
                record.requested_by.name if record.requested_by else False
            )
            record.done_by_name = record.done_by.name if record.done_by else False

    @api.depends_context("tz")
    def _compute_reviewed_formated_date(self):
        timezone = self._context.get("tz") or self.env.user.partner_id.tz or "UTC"
        for review in self:
            if not review.reviewed_date:
                review.reviewed_formated_date = False
                continue
            reviewed_date_utc = pytz.timezone("UTC").localize(review.reviewed_date)
            reviewed_date_tz = reviewed_date_utc.astimezone(pytz.timezone(timezone))
            review.reviewed_formated_date = reviewed_date_tz.replace(tzinfo=None)

    @api.depends("definition_id.approve_sequence")
    def _compute_can_review(self):
        reviews = self.filtered(lambda rev: rev.status in ["waiting", "pending"])
        if reviews:
            # get minimum sequence of all to prevent jumps
            next_seq = min(reviews.mapped("sequence"))
            for record in reviews:
                # if approve by sequence, check sequence has been reached
                if record.approve_sequence:
                    if record.sequence == next_seq:
                        record.status = "pending"
                # if there is no approval sequence go directly to pending state
                elif not record.approve_sequence:
                    record.status = "pending"
                if record.status == "pending":
                    if record.definition_id.notify_on_pending:
                        record._notify_pending_status(record)
        for record in self:
            record.can_review = record._can_review_value()

    def _can_review_value(self):
        if self.status not in ("pending", "waiting"):
            return False
        if not self.approve_sequence:
            return True
        resource = self.env[self.model].browse(self.res_id)
        reviews = resource.review_ids.filtered(lambda r: r.status == "pending")
        if not reviews:
            return True
        sequence = min(reviews.mapped("sequence"))
        return self.sequence == sequence

    @api.model
    def _get_reviewer_fields(self):
        return ["reviewer_id", "reviewer_group_id", "reviewer_group_id.user_ids"]

    @api.depends(lambda self: self._get_reviewer_fields())
    def _compute_reviewer_ids(self):
        for rec in self:
            rec.reviewer_ids = rec._get_reviewers()

    @api.depends("reviewer_ids")
    def _compute_todo_by(self):
        """Show by group or by abbrev list of names"""
        num_show = 3  # Max number of users to display
        for rec in self:
            todo_by = False
            if rec.reviewer_group_id:
                todo_by = self.env._("Group %s", rec.reviewer_group_id.name)
            else:
                todo_by = ", ".join(rec.reviewer_ids[:num_show].mapped("display_name"))
                num_users = len(rec.reviewer_ids)
                if num_users > num_show:
                    todo_by = f"{todo_by} (and {num_users - num_show} more)"
            rec.todo_by = todo_by

    def _get_reviewers(self):
        if self.reviewer_id or self.reviewer_group_id.user_ids:
            return self.reviewer_id + self.reviewer_group_id.user_ids
        reviewer_field = self.env["res.users"]
        if self.reviewer_field_id:
            resource = self.env[self.model].browse(self.res_id)
            reviewer_field = getattr(resource, self.reviewer_field_id.name, False)
            if not reviewer_field or not reviewer_field._name == "res.users":
                raise ValidationError(
                    self.env._("There are no res.users in the selected field")
                )
        return reviewer_field

    def _notify_pending_status(self, review_ids):
        """Method to call and reuse abstract notification method"""
        resource = self.env[self.model].browse(self.res_id)
        resource._notify_review_available(review_ids)

    def _get_reminder_notification_subtype(self):
        return "base_tier_validation.mt_tier_validation_reminder"

    def _get_reminder_activity_type(self):
        return "base_tier_validation.mail_act_tier_validation_reminder"

    def _notify_review_reminder_body(self):
        delay = (fields.Datetime.now() - self.create_date).days
        return self.env._("A review has been requested %s days ago.", delay)

    def _send_review_reminder(self):
        record = self.env[self.model].browse(self.res_id)
        # Only schedule activity if reviewer is a single user and model has activities
        if len(self.reviewer_ids) == 1 and hasattr(record, "activity_ids"):
            self._schedule_review_reminder_activity(record)
        elif hasattr(record, "message_post"):
            self._notify_review_reminder(record)
        else:
            msg = f"Could not send reminder for record {record}"
            _logger.exception(msg)
        self.last_reminder_date = fields.Datetime.now()

    def _notify_review_reminder(self, record):
        record.message_post(
            subtype_xmlid=self._get_reminder_notification_subtype(),
            body=self._notify_review_reminder_body(),
        )

    def _schedule_review_reminder_activity(self, record):
        record.activity_schedule(
            act_type_xmlid=self._get_reminder_activity_type(),
            note=self._notify_review_reminder_body(),
            user_id=self.reviewer_ids.id,
        )
