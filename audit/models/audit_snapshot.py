"""Classes and backend functionality for Audit module"""

import asyncio
from datetime import datetime
import json
import logging
from math import ceil

import pytz

from odoo import models, fields, api
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


# Copy the snapshot IDs across
# UPDATE audit_snapshot_question
# SET snapshot_id = audit_snapshot.id
# FROM audit_snapshot
# JOIN audit_snapshot_section ON audit_snapshot.id = audit_snapshot_section.snapshot_id
# WHERE audit_snapshot_question.snapshot_section_id = audit_snapshot_section.id


# Need start and end date times for the day in NZ
# This date_str will be in yyyy-mm-dd format
def convert_nz_to_utc(date_str):
    """
    Thank you chatgpt
    """
    time_format = "%Y-%m-%d %H:%M:%S.%f"

    # Define the time zones
    nz_tz = pytz.timezone("Pacific/Auckland")
    utc_tz = pytz.utc

    # Parse the input date string as yyyy-mm-dd
    nz_start_time = datetime.strptime(date_str + " 00:00:00.999", time_format)
    nz_end_time = datetime.strptime(date_str + " 23:59:59.999", time_format)

    # Localize the datetime to New Zealand time zone (to consider daylight saving)
    nz_start_time = nz_tz.localize(nz_start_time)
    nz_end_time = nz_tz.localize(nz_end_time)

    # Convert to UTC
    utc_start_time = nz_start_time.astimezone(utc_tz)
    utc_end_time = nz_end_time.astimezone(utc_tz)

    # Return the UTC time in the same yyyy-mm-dd format
    return {
        "utc_start_time": utc_start_time.strftime(time_format),
        "utc_end_time": utc_end_time.strftime(time_format),
    }


class SnapshotSection(models.Model):
    """SnapshotSection class, a SnapshotSection is made from every Section of an audit."""

    _name = "audit.snapshot_section"
    _description = "We copy the section at the time the audit snapshot is created"

    original_section_id = fields.Many2one(comodel_name="audit.section")
    name = fields.Text()
    snapshot_question_ids = fields.One2many(
        comodel_name="audit.snapshot_question",
        inverse_name="snapshot_section_id",
        string="Questions",
    )
    domain_id = fields.Many2one(
        comodel_name="audit.domain", string="Domain", required=True
    )
    snapshot_id = fields.Many2one(
        comodel_name="audit.snapshot", string="Audit Snapshot"
    )

    # If each section counts their questions correct, we can pass these up to compute overall score
    # as well as section score
    maximum_section_score = fields.Float(
        compute="_compute_maximum_section_score", store=True
    )

    @api.depends("snapshot_question_ids")
    def _compute_maximum_section_score(self):
        for record in self:
            record.maximum_section_score = 0.0
            for question in record.snapshot_question_ids:
                record.maximum_section_score += 1

    actual_section_score = fields.Float(
        compute="_compute_actual_section_score", store=True
    )

    @api.depends("snapshot_question_ids", "snapshot_question_ids.value")
    def _compute_actual_section_score(self):
        for record in self:
            record.actual_section_score = 0.0
            for question in record.snapshot_question_ids:
                record.actual_section_score += question.value

    percentage_section_score = fields.Float(
        compute="_compute_percentage_section_score", store=True
    )

    @api.depends("actual_section_score", "maximum_section_score")
    def _compute_percentage_section_score(self):
        for record in self:
            if record.maximum_section_score == 0:
                record.percentage_section_score = 0
            else:
                record.percentage_section_score = round(
                    (record.actual_section_score / record.maximum_section_score), 2
                )


class SnapshotQuestion(models.Model):
    """SnapshotQuestion class, a SnapshotQuestion is created for every Question class of an Audit."""

    _name = "audit.snapshot_question"
    _description = "Copy of the question"

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
        comodel_name="audit.snapshot_section", string="Section", required=True
    )
    original_question_id = fields.Many2one(comodel_name="audit.question")
    prompt = fields.Text()
    answer_type = fields.Char(required=True)

    answer_yn = fields.Selection(selection=ANSWER_SELECTION)
    answer_star = fields.Selection(selection=STAR_SELECTION)
    answer_perc = fields.Float()  # min=0, max=100
    # All questions are by default applicable, hence default=True
    applicable = fields.Boolean(string="applicable", default=True)
    comment = fields.Text()
    image = fields.Image(string="image")
    value = fields.Float(compute="_compute_value")

    @api.depends("answer_yn", "answer_star", "answer_perc")
    def _compute_value(recordset):
        for record in recordset:
            record.value = (
                float(record.answer_yn)
                + (float(record.answer_star) / 4)
                + (record.answer_perc / 100)
            )

    @api.model
    def toggle_not_applicable(self, *args, **kwargs):
        """
        Toggle the applicable field for the question.
        Checks to see if snapshot is locked or not.
        """
        snapshot_question = self.env["audit.snapshot_question"].browse(args[0])
        # if not snapshot_question.snapshot_id.locked: # this requirement was removed
        snapshot_question.applicable = not snapshot_question.applicable
        return {"id": snapshot_question.id, "applicable": snapshot_question.applicable}


class Snapshot(models.Model):
    """Snapshot class, when an Audit instance is audit, a Snapshot instance is created for that Audit."""

    _name = "audit.snapshot"
    _description = "Performing an audit creates a 'snapshot' of the item being audited."
    _order = "date_conducted desc"

    domain_id = fields.Many2one(comodel_name="audit.domain", string="Domain")
    target_id = fields.Many2one(
        comodel_name="audit.target", string="Target", required=True
    )
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

    locked = fields.Boolean(string="locked", default=False)
    name = fields.Text(compute="_compute_name")
    maximum_score = fields.Float(compute="_compute_maximum_score")
    actual_score = fields.Float(compute="_compute_actual_score")
    # percentage_score, a combination of overall score for each section - can never be more than 100%
    percentage_score = fields.Float(compute="_compute_percentage_score", store=True)
    # Calculate how many of the snapshot questions for this snapshot had comments added to them
    questions_with_comments = fields.Integer(compute="_compute_questions_with_comments")
    # Instances with status as active have not been archived
    active = fields.Boolean("Active", default=True)

    search_text = fields.Char(compute="_compute_search_text", store=True)
    team_id = fields.Many2one(
        comodel_name="audit.team", string="Team", ondelete="restrict", required=False
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
            if (
                snapshot_question["snapshot_section_id"][1]
                not in _sections_and_questions.keys()  # pylint: disable=consider-iterating-dictionary
            ):
                _sections_and_questions[
                    snapshot_question["snapshot_section_id"][1]
                ] = []

        for snapshot_question in snapshot_questions:
            _sections_and_questions.get(
                snapshot_question["snapshot_section_id"][1], None
            ).append(snapshot_question)

        return {
            "sections": [section.name for section in self.snapshot_section_ids],
            "questions": _sections_and_questions,
            "all_locked": self.locked,
        }

    @api.depends("domain_id", "target_id")
    def _compute_search_text(self):
        """
        Computed property for searching might seem like a good idea until unrelated things break.
        Please do not remove the str() conversions, this property fires during the creation
        process of a new snapshot, it's totally unrelated, but it causes the snapshot creation
        process to break in odoo-test and odoo-prod - Locally, no issues
        """
        for record in self:
            try:
                record.search_text = ""

                if record.domain_id:
                    domain_name = record.domain_id.name
                    if isinstance(domain_name, bool):
                        domain_name = str(domain_name)
                    record.search_text += str(domain_name)

                if record.target_id:
                    target_name = record.target_id.name
                    if isinstance(target_name, bool):
                        target_name = str(target_name)
                    record.search_text += str(target_name)

                if record.inspector_id:
                    inspector_name = record.inspector_id.name
                    if isinstance(inspector_name, bool):
                        inspector_name = str(inspector_name)
                    record.search_text += str(inspector_name)

            except Exception as e:
                _logger.error(
                    "Snapshot::_compute_search_text > Error computing search text for record %s: %s",
                    record.id,
                    str(e),
                )
                # Raise the exception to make the error visible
                raise UserError(
                    f"Failed to compute search text for snapshot {record.id}: {str(e)}"
                ) from e

    # What we'll do here, is, loop through all sections and questions, and copy them into the snapshot
    @api.model
    def create(self, vals):
        """Overriding the create function."""
        # Handle both single dict and list of dicts
        if isinstance(vals, list):
            # If it's a list, process the first item (should only be one for this use case)
            vals = vals[0] if vals else {}

        # We can supply existing links
        domain_id = vals.get("domain_id", None)
        target_id = vals.get("target_id", None)
        inspector_id = vals.get("inspector_id", None)
        # Or we can create some
        new_target_name = vals.get("new_target_name", None)
        new_inspector_name = vals.get("new_inspector_name", None)

        if domain_id is None:
            raise UserError("Must supply domain")
        if target_id is None and new_target_name is None:
            raise UserError("Must supply target or target name")
        if target_id is None and new_target_name is not None:
            target = self.env["audit.target"].create(
                {
                    "name": new_target_name,
                    "domain_rel_ids": [domain_id],
                }
            )
            target_id = target.id
        if inspector_id is None and new_inspector_name is None:
            raise UserError("Must supply inspector or inspector name")
        if inspector_id is None and new_inspector_name is not None:
            inspector = self.env["audit.inspector"].create(
                {
                    "forename": new_inspector_name["forename"],
                    "surname": new_inspector_name["surname"],
                }
            )
            inspector_id = inspector.id

        # Create the snapshot and then create and link snapshot_sections & snapshot_questions
        # Get team_id from original vals, or use first available team as fallback
        team_id = vals.get("team_id")
        if not team_id:
            team = self.env["audit.team"].search([], limit=1)
            team_id = team.id if team else None

        new_snapshot = super(Snapshot, self).create(
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
        # Snapshot sections & Snapshot questions created, calculate new snapshot's maximum score
        # This will not get triggered by the listeners
        new_snapshot._compute_maximum_score()
        _logger.info(f"Snapshot::create > After _compute_maximum_score {new_snapshot}")
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
    def _compute_maximum_score(snapshots):  # pylint disable=no-self-use
        """
        Without you knowing, this computed property will retrieve every snapshot there is and try and compute
        it's `maximum_score` and thus confuse itself.  Hence why this ugly looping business takes place in order
        to avoid `Singleton` errors.
        """
        for snapshot in snapshots:
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
    def _compute_actual_score(snapshots):  # pylint disable=no-self-use
        """
        Add up only correct answers.
        """
        for snapshot in snapshots:
            snapshot.actual_score = 0
            for section in snapshot.snapshot_section_ids:
                for question in section.snapshot_question_ids:
                    if question.applicable:
                        snapshot.actual_score += question.value

    @api.depends("actual_score", "maximum_score")
    def _compute_percentage_score(snapshots):
        for snapshot in snapshots:
            if snapshot.maximum_score == 0:
                snapshot.percentage_score = 0
            else:
                # This field is displayed by a widget, the widget converts correctly between decimal and float
                snapshot.percentage_score = round(
                    (snapshot.actual_score / snapshot.maximum_score), 2
                )

    def snapshot_percentage_score(self, snapshots: list):
        """
        Combined public method of `_compute_actual_score`, `_compute_maximum_score` & `_compute_percentage_score`.
        We trigger this from the front-end to only update the ones we want.
        """
        for snapshot in snapshots:
            # Find the snapshot object
            snapshot: object = self.env["audit.snapshot"].search(
                [("id", "=", snapshot.get("id"))]
            )
            # Calculate the maximum score & actual_score for the snapshot to avoid divisions by zero
            # pylint: disable=protected-access
            snapshot._compute_actual_score()
            snapshot._compute_maximum_score()
            snapshot._compute_percentage_score()
            # pylint: enable=protected-access

    @api.depends("snapshot_section_ids")
    def _compute_questions_with_comments(snapshots):  # pylint disable=no-self-use
        """For a Snapshot, if submitted, calculate how many of its questions had comments added to them."""
        for snapshot in snapshots:
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

    # We need a search API to help drive the frontend.  It needs to be quite flexible but also efficient.
    # Any search will only ever return paginated data.  The parameters it gets is a stringified json object
    # of search terms
    PAGE_SIZE = 15
    PASS_THRESHOLD = 0.85

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
                    "search_text",
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
        if search_object.get("searchDate"):
            # Convert to UTC start and end dates.
            # Because NZ days start and end at midnight to midnight, so UTC equivalent is halfway
            # between the days
            utc_dates = convert_nz_to_utc(search_object.get("searchDate"))
            search_query.append(("date_conducted", ">=", utc_dates["utc_start_time"]))
            search_query.append(("date_conducted", "<=", utc_dates["utc_end_time"]))

        # We need to make these conditions overlapping, so all must be met to filter.
        for _i in range(0, len(search_query) - 1):
            search_query.insert(0, "&")

        # Get count (to compute page number)
        snapshot_count = self.env["audit.snapshot"].search_count(search_query)
        page_count = ceil(snapshot_count / self.PAGE_SIZE)
        # If page number submitted is too high, fix that
        page_number = search_object.get("searchPage")
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
            2. Logged-in user is a team leader -> return snapshots done by inspectors and leaders of the team leaders team
            3. Logged-in user is not a team leader -> return snapshots done by the logged-in user
            4. Logged-in user has no team and no inspector object -> return no snapshots
        """
        logged_in_user = self.env.user
        admin_user = logged_in_user.has_group(
            "base.group_system"
        )  # Users/Administration/Settings
        # If the user is an admin user then they should see all snapshots
        offset = ((page_number - 1) * self.PAGE_SIZE) if page_number > 0 else 0
        if admin_user:
            return self.env["audit.snapshot"].search_read(
                search_query,
                limit=self.PAGE_SIZE,
                offset=offset,
                order="date_conducted desc",
            ), self.env["audit.snapshot"].search_count(([("active", "=", True)]))

        # Try and find an inspector that has a res.user or res.partner object linked to the logged-in user
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

        team = inspector and self.env["audit.team"].search(["|", ("team_member_ids", "in", inspector.id), ("team_leader_ids", "in", inspector.id)])
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
                    offset=offset,
                    order="date_conducted desc",
                ), self.env["audit.snapshot"].search_count(
                    (
                        [
                            ("active", "=", True),
                            (
                                "inspector_id",
                                "in",
                                set(team_members.ids + team_leader.ids),
                            ),
                        ]
                    )
                )

            if inspector.id not in team_leader.ids:  # Logged-in user not a team leader
                return self.env["audit.snapshot"].search_read(
                    [("inspector_id", "=", inspector.id)],
                    limit=self.PAGE_SIZE,
                    offset=offset,
                    order="date_conducted desc",
                ), self.env["audit.snapshot"].search_count(
                    ([("active", "=", True), ("inspector_id", "=", inspector.id)])
                )

            return [], 0

        if inspector and not team:  # Inspector not part of a team
            return self.env["audit.snapshot"].search_read(
                [("inspector_id", "=", inspector.id)],
                limit=self.PAGE_SIZE,
                offset=offset,
                order="date_conducted desc",
            ), self.env["audit.snapshot"].search_count(
                ([("active", "=", True), ("inspector_id", "=", inspector.id)])
            )

        return [], 0
