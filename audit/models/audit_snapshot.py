"""Classes and backend functionality for Audit module"""

import json
import logging
from datetime import datetime
from math import ceil

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SnapshotSection(models.Model):
    """
    Section copy: each `audit.section` in a domain becomes a snapshot section.
    """

    _name = "audit.snapshot_section"
    _description = "Copy of AuditSection"

    name = fields.Text()
    original_section_id = fields.Many2one(comodel_name="audit.section")
    snapshot_question_ids = fields.One2many(
        comodel_name="audit.snapshot_question",
        inverse_name="snapshot_section_id",
        string="Questions",
    )
    domain_id = fields.Many2one(comodel_name="audit.domain", required=True)
    snapshot_id = fields.Many2one(
        comodel_name="audit.snapshot", string="Audit Snapshot"
    )

    # If each section counts their questions correct, we can pass these up to
    # compute overall score and section score
    maximum_section_score = fields.Float(
        compute="_compute_maximum_section_score", store=True
    )
    actual_section_score = fields.Float(
        compute="_compute_actual_section_score", store=True
    )
    percentage_section_score = fields.Float(
        compute="_compute_percentage_section_score", store=True
    )

    @api.depends("snapshot_question_ids")
    def _compute_maximum_section_score(self):
        for record in self:
            record.maximum_section_score = 0.0
            for _ in record.snapshot_question_ids:
                record.maximum_section_score += 1

    @api.depends("snapshot_question_ids", "snapshot_question_ids.value")
    def _compute_actual_section_score(self):
        for record in self:
            record.actual_section_score = 0.0
            for question in record.snapshot_question_ids:
                record.actual_section_score += question.value

    @api.depends("actual_section_score", "maximum_section_score")
    def _compute_percentage_section_score(self):
        for record in self:
            if record.maximum_section_score == 0:
                record.percentage_section_score = 0
            else:
                # Field shown by a widget; widget maps decimal and float.
                record.percentage_section_score = round(
                    (record.actual_section_score / record.maximum_section_score), 2
                )


class SnapshotQuestion(models.Model):
    """One snapshot question per source question, linked to a snapshot section."""

    _name = "audit.snapshot_question"
    _description = "Copy of AuditQuestion"

    YES = "1"
    NO = "0"

    ANSWER_SELECTION = [(YES, "Yes"), (NO, "No")]

    ONE_STAR = "1"
    TWO_STAR = "2"
    THREE_STAR = "3"
    FOUR_STAR = "4"

    STAR_SELECTION = [
        (ONE_STAR, "*"),
        (TWO_STAR, "* *"),
        (THREE_STAR, "* * *"),
        (FOUR_STAR, "* * * *"),
    ]

    snapshot_id = fields.Many2one(comodel_name="audit.snapshot")
    snapshot_section_id = fields.Many2one(
        comodel_name="audit.snapshot_section", required=True
    )
    original_question_id = fields.Many2one(comodel_name="audit.question")
    prompt = fields.Text()
    answer_type = fields.Char(required=True)

    answer_yn = fields.Selection(selection=ANSWER_SELECTION)
    answer_star = fields.Selection(selection=STAR_SELECTION)
    answer_perc = fields.Float()  # min=0, max=100
    # All questions are by default applicable, hence default=True
    applicable = fields.Boolean(default=True)
    image = fields.Image()
    value = fields.Float(compute="_compute_value")
    comment = fields.Text()

    @api.depends("answer_yn", "answer_star", "answer_perc")
    def _compute_value(self):
        for record in self:
            record.value = (
                float(record.answer_yn)
                + (float(record.answer_star) / 4)
                + (record.answer_perc / 100)
            )

    @api.model
    def toggle_not_applicable(self, snapshot_question_id, **_kwargs):
        """Toggle the applicable field for the question."""
        snapshot_question = self.env["audit.snapshot_question"].browse(
            snapshot_question_id
        )
        snapshot_question.applicable = not snapshot_question.applicable
        return {"id": snapshot_question.id, "applicable": snapshot_question.applicable}

    def write(self, vals):
        """
        Strip ``data:<mime>;base64,`` prefix from dashboard data URLs; pass through
        other values unchanged.
        """
        if "image" in vals and vals.get("image") is not False and vals.get("image"):
            image_val = str(vals["image"])
            if image_val.lstrip().startswith("data:") and "," in image_val:
                vals = dict(vals)
                vals["image"] = image_val.split(",", 1)[1]
        return super().write(vals)


class Snapshot(models.Model):
    """Records one completed audit (scores, sections, and questions) for a target."""

    _name = "audit.snapshot"
    _description = "Performing an audit creates a 'snapshot' of the item being audited."
    _order = "date_conducted desc"

    # Maximum amount of Snapshot instances displayed on each page of the Dashboard
    PAGE_SIZE = 10
    # Score a Snapshot must achieve before it will display as `Passed`, else `Fail`
    PASS_THRESHOLD = 0.85

    domain_id = fields.Many2one(comodel_name="audit.domain")
    target_id = fields.Many2one(comodel_name="audit.target", required=True)
    date_conducted = fields.Datetime(default=datetime.today())
    inspector_id = fields.Many2one(
        comodel_name="audit.inspector", string="Inspector / Manager", required=True
    )
    notes = fields.Text()
    snapshot_section_ids = fields.One2many(
        comodel_name="audit.snapshot_section",
        inverse_name="snapshot_id",
        string="Sections",
        required=True,
    )

    locked = fields.Boolean(default=False)
    # Stored so `custom_search` can filter with SQL (`ilike` on computed-only fields
    # raises "not stored" in Odoo 19+).
    name = fields.Text(compute="_compute_name", store=True)
    maximum_score = fields.Float(compute="_compute_maximum_score")
    actual_score = fields.Float(compute="_compute_actual_score")
    # Overall score for each section combined; cannot exceed 100%.
    percentage_score = fields.Float(compute="_compute_percentage_score", store=True)
    # Count of snapshot questions on this snapshot that have comments
    questions_with_comments = fields.Integer(compute="_compute_questions_with_comments")
    # Instances with status as active have not been archived
    active = fields.Boolean(default=True)
    team_id = fields.Many2one(
        comodel_name="audit.team", ondelete="restrict", required=False
    )

    def get_snapshot_questions(self):
        """Get the questions for a particular snapshot."""
        snapshot = self
        if not snapshot:
            return {}

        snapshot.ensure_one()
        snapshot_questions = self.env["audit.snapshot_question"].search_read(
            [("snapshot_section_id", "in", snapshot.snapshot_section_ids.ids)]
        )
        _sections_and_questions = {}
        for snapshot_question in snapshot_questions:
            section_label = snapshot_question["snapshot_section_id"][1]
            if section_label not in _sections_and_questions:
                _sections_and_questions[section_label] = []

        for snapshot_question in snapshot_questions:
            _sections_and_questions.get(
                snapshot_question["snapshot_section_id"][1], None
            ).append(snapshot_question)

        return {
            "sections": [section.name for section in self.snapshot_section_ids],
            "questions": _sections_and_questions,
            "all_locked": self.locked,
        }

    @api.model
    def create(self, vals):
        """Overriding the create function."""
        # Handle both single dict and list of dicts
        if isinstance(vals, list):
            vals = vals[0] if vals else {}

        # Get the critical values a new Snapshot will need
        domain_id = vals.get("domain_id", None)
        target_id = vals.get("target_id", None)
        inspector_id = vals.get("inspector_id", None)

        if any(value is None for value in (domain_id, target_id, inspector_id)):
            raise UserError(
                self.env._(
                    "None of Domain ID: %(domain_id)s, Target ID: %(target_id)s, "
                    "or Inspector ID: %(inspector_id)s may be none.",
                    domain_id=domain_id,
                    target_id=target_id,
                    inspector_id=inspector_id,
                )
            )

        # Get team_id from original vals, or use first available team as fallback
        team_id = vals.get("team_id")
        if not team_id:
            team = self.env["audit.team"].search([], limit=1)
            team_id = team.id if team else None

        try:
            # Create snapshot, then snapshot_sections and snapshot_questions
            new_snapshot = super().create(
                {
                    "domain_id": domain_id,
                    "target_id": target_id,
                    "inspector_id": inspector_id,
                    "team_id": team_id,
                }
            )

            # Now create snapshot_sections for each section linked to the domain id.
            current_sections = self.env["audit.section"].search(
                domain=[("domain_id", "=", domain_id)]
            )
            if not current_sections:
                raise UserError(
                    self.env._(
                        "The chosen domain has no sections. Add sections and questions "
                        "for domain_id %(domain_id)s first.",
                        domain_id=domain_id,
                    )
                )

            for section in current_sections:
                snapshot_section = self.env["audit.snapshot_section"].create(
                    {
                        "original_section_id": section.id,
                        "name": section.name,
                        "domain_id": domain_id,
                        "snapshot_id": new_snapshot.id,
                    }
                )
                current_questions = self.env["audit.question"].search(
                    domain=[("section_id", "=", section.id)]
                )
                if not current_questions:
                    raise UserError(
                        self.env._(
                            "The chosen section has no questions. Create questions for "
                            "section_id %(section_id)s first.",
                            section_id=section.id,
                        )
                    )

                for question in current_questions:
                    self.env["audit.snapshot_question"].create(
                        {
                            "original_question_id": question.id,
                            "snapshot_id": new_snapshot.id,
                            "prompt": question.prompt,
                            "snapshot_section_id": snapshot_section.id,
                            "answer_type": question.answer_type,
                        }
                    )

            # pylint: disable=protected-access
            # Sections and questions are created; compute the snapshot maximum score
            # (not triggered by the listeners)
            new_snapshot._compute_maximum_score()
            _logger.info(
                "Snapshot::create > After _compute_maximum_score %s", new_snapshot
            )
        except Exception as e:
            _logger.exception("Snapshot could not be created")
            raise UserError(
                self.env._("Snapshot could not be created: %s", str(e))
            ) from e
        return new_snapshot

    @api.depends("target_id", "target_id.name", "date_conducted")
    def _compute_name(self):
        for record in self:
            if record.target_id:
                record.name = "{} [{}]".format(
                    record.target_id.name, record.date_conducted.strftime("%y-%m-%d")
                )

            else:
                record.name = "Unnamed Snapshot"

    @api.depends(
        "snapshot_section_ids",
        "snapshot_section_ids.snapshot_question_ids",
        "snapshot_section_ids.snapshot_question_ids.applicable",
    )
    def _compute_maximum_score(self):
        """
        Loop records explicitly to avoid computing on unrelated snapshots
        and triggering singleton issues.
        """
        for snapshot in self:
            snapshot.maximum_score = 0
            for section in snapshot.snapshot_section_ids:
                for question in section.snapshot_question_ids:
                    if question.applicable:
                        snapshot.maximum_score += 1

    @api.depends(
        "snapshot_section_ids",
        "snapshot_section_ids.snapshot_question_ids",
        "snapshot_section_ids.snapshot_question_ids.value",
    )
    def _compute_actual_score(self):
        """
        Add up only correct answers.
        """
        for snapshot in self:
            snapshot.actual_score = 0
            for section in snapshot.snapshot_section_ids:
                for question in section.snapshot_question_ids:
                    if question.applicable:
                        snapshot.actual_score += question.value

    @api.depends("actual_score", "maximum_score")
    def _compute_percentage_score(self):
        for snapshot in self:
            if snapshot.maximum_score == 0:
                snapshot.percentage_score = 0
            else:
                # Shown in UI via a custom widget; handles decimal and float.
                snapshot.percentage_score = round(
                    (snapshot.actual_score / snapshot.maximum_score), 2
                )

    def snapshot_percentage_score(self, snapshots: list):
        """
        Re-run score computes for a subset of snapshot dicts (dashboard RPC).

        Calls the same compute methods the ORM would use, for records selected
        in the UI.
        """
        for snapshot in snapshots:
            # Find the snapshot object
            snapshot: object = self.env["audit.snapshot"].search(
                [("id", "=", snapshot.get("id"))]
            )
            # Recompute max and actual score so we never divide by zero
            # pylint: disable=protected-access
            snapshot._compute_actual_score()
            snapshot._compute_maximum_score()
            snapshot._compute_percentage_score()
            # pylint: enable=protected-access

    @api.depends("snapshot_section_ids")
    def _compute_questions_with_comments(self):
        """Count questions with comments when the snapshot is locked (submitted)."""
        for snapshot in self:
            snapshot.questions_with_comments = 0

            if snapshot.read()[0]["locked"]:
                snapshot_questions = snapshot.env["audit.snapshot_question"].search(
                    [
                        (
                            "snapshot_section_id",
                            "in",
                            snapshot.read()[0]["snapshot_section_ids"],
                        )
                    ]
                )
                for snapshot_question in snapshot_questions:
                    if snapshot_question.read()[0]["comment"]:
                        snapshot.questions_with_comments += 1

    @api.model
    def custom_search(self, search_string):
        """
        This helps search for audits
        """
        _logger.info(search_string)
        search_object = json.loads(search_string)
        search_query = [("active", "=", True)]
        # Search name
        if search_object.get("searchText"):
            search_query.append(
                (
                    "name",
                    "ilike",
                    "%" + str(search_object.get("searchText")) + "%",
                )
            )
        # Search status
        if search_object.get("searchStatus"):
            if str(search_object.get("searchStatus")) == "PASS":
                search_query.append(("percentage_score", ">=", self.PASS_THRESHOLD))
            elif str(search_object.get("searchStatus")) == "FAIL":
                search_query.append(("percentage_score", "<", self.PASS_THRESHOLD))

        # We need to make these conditions overlapping, so all must be met to filter.
        for _i in range(0, len(search_query) - 1):
            search_query.insert(0, "&")

        # Get count (to compute page number)
        snapshot_count = self.env["audit.snapshot"].search_count(search_query)
        page_count = ceil(snapshot_count / self.PAGE_SIZE)
        # If page number submitted is too high, fix that
        page_number = search_object.get("searchPage") or 1
        if page_number > page_count > 0:
            page_number = page_count

        # Get data
        logged_in_user_snapshosts, logged_in_user_snapshosts_count = (
            self.snapshots_per_user(search_query=search_query, page_number=page_number)
        )

        # Update the snapshots in question before returning them
        self.snapshot_percentage_score(logged_in_user_snapshosts)

        return {
            "snapshots": logged_in_user_snapshosts,
            "numberOfPages": ceil(logged_in_user_snapshosts_count / self.PAGE_SIZE),
            "newPageNumber": page_number,
        }

    # pylint: disable=too-many-return-statements
    def snapshots_per_user(
        self, search_query: list, page_number: int
    ) -> tuple[list, int]:
        """
        Return Snapshots according to the following logic:

            1. Logged-in user is an Admin user -> return all snapshots
            2. Logged-in user is a team leader -> return snapshots done by
               inspectors and leaders of the team leader's team
            3. Logged-in user is not a team leader -> return snapshots for the
               logged-in user only
            4. Logged-in user has no team and no inspector object -> no snapshots
        """
        logged_in_user = self.env.user
        admin_user = logged_in_user.has_group("base.group_system")

        # If the user is an admin user then they should see all snapshots
        if admin_user:
            return self.env["audit.snapshot"].search_read(
                search_query,
                limit=self.PAGE_SIZE,
                offset=(page_number - 1) * self.PAGE_SIZE,
                order="date_conducted desc",
            ), self.env["audit.snapshot"].search_count([("active", "=", True)])

        # Find inspector by system user or partner; otherwise no data.
        inspector = self.env["audit.inspector"].search(
            [
                "|",
                ("res_user_id", "=", logged_in_user.id),
                ("partner_id", "=", logged_in_user.partner_id.id),
            ],
            limit=1,
        )

        # No inspector?  no snapshots
        if not inspector:
            return [], 0

        team = inspector and self.env["audit.team"].search(
            [
                "|",
                ("team_member_ids", "in", inspector.id),
                ("team_leader_ids", "in", inspector.id),
            ]
        )
        team_leader = team and team.team_leader_ids
        team_members = team and team.team_member_ids

        if inspector and team:
            if inspector.id in team_leader.ids:  # Logged-in user is a team leader
                return self.env["audit.snapshot"].search_read(
                    [
                        (
                            "inspector_id",
                            "in",
                            list(set(team_members.ids + team_leader.ids)),
                        )
                    ],
                    limit=self.PAGE_SIZE,
                    offset=(page_number - 1) * self.PAGE_SIZE,
                    order="date_conducted desc",
                ), self.env["audit.snapshot"].search_count(
                    [
                        ("active", "=", True),
                        (
                            "inspector_id",
                            "in",
                            set(team_members.ids + team_leader.ids),
                        ),
                    ]
                )

            if inspector.id not in team_leader.ids:  # Logged-in user not a team leader
                return self.env["audit.snapshot"].search_read(
                    [("inspector_id", "=", inspector.id)],
                    limit=self.PAGE_SIZE,
                    offset=(page_number - 1) * self.PAGE_SIZE,
                    order="date_conducted desc",
                ), self.env["audit.snapshot"].search_count(
                    [("active", "=", True), ("inspector_id", "=", inspector.id)]
                )

            return [], 0

        if inspector and not team:  # Inspector not part of a team
            return self.env["audit.snapshot"].search_read(
                [("inspector_id", "=", inspector.id)],
                limit=self.PAGE_SIZE,
                offset=(page_number - 1) * self.PAGE_SIZE,
                order="date_conducted desc",
            ), self.env["audit.snapshot"].search_count(
                [("active", "=", True), ("inspector_id", "=", inspector.id)]
            )

        return [], 0
