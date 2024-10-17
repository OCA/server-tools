# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class ScheduleDay(models.Model):
    _name = "schedule.day"
    _description = "Schedule specific days within a year"

    name = fields.Char(required=True)

    weekday_ids = fields.Many2many("schedule.weekday")

    start_date = fields.Date(required=True, default=lambda self: date.today())

    mode = fields.Selection(
        [
            ("weekly", _("Weekly")),
            ("monthly", _("Monthly")),
            ("yearly", _("Yearly")),
        ],
        required=True,
        default="weekly",
    )

    step = fields.Integer(
        required=True,
        default=1,
        string="Interval",
    )

    nth_weekday = fields.Selection(
        [
            ("0", _("First")),
            ("1", _("Second")),
            ("2", _("Third")),
            ("3", _("Fourth")),
            ("last", _("Last")),
        ],
        required=True,
        default="0",
    )

    yearly_month = fields.Selection(
        [
            ("1", _("January")),
            ("2", _("February")),
            ("3", _("March")),
            ("4", _("April")),
            ("5", _("May")),
            ("6", _("June")),
            ("7", _("July")),
            ("8", _("August")),
            ("9", _("September")),
            ("10", _("October")),
            ("11", _("November")),
            ("12", _("December")),
        ],
        required=True,
        default="1",
        string="Month",
    )

    preview = fields.Char(
        compute="_compute_preview",
        string="Preview",
    )

    def is_scheduled(self, day=None):
        if len(self) == 0:
            return True

        self.ensure_one()

        if not day:
            day = date.today()

        # Check if weekday is correct
        if self.weekday_ids and not self.weekday_ids.filtered_domain(
            [("number", "=", day.weekday())]
        ):
            return False

        if self.mode == "weekly":
            # Check if week is correct
            dweeks = (day - self.start_date).days // 7

            if dweeks % self.step != 0:
                return False

            return True
        elif self.mode == "monthly":
            # Check if month is correct
            r = relativedelta(day, self.start_date)
            dmonths = r.years * 12 + r.months

            if dmonths % self.step != 0:
                return False
        elif self.mode == "yearly" and day.month != int(self.yearly_month):
            return False

        # Special case last day of month
        if self.nth_weekday == "last":
            month_end_delta = calendar.monthrange(day.year, day.month)[1] - day.day

            if month_end_delta > 6:
                return False
        elif (day.day - 1) // 7 != int(self.nth_weekday):
            return False

        return True

    @api.depends(
        "weekday_ids", "start_date", "mode", "step", "nth_weekday", "yearly_month"
    )
    def _compute_preview(self):
        today = date.today()

        for record in self:
            preview_dates = []

            if record.mode == "yearly":
                year = today.year
                month = int(self.yearly_month)
                day = today.day if month == today.month else 1

                # Skip year if month is in the past
                if month < today.month:
                    year += 1

                for year in range(year, year + 5):
                    num_days = calendar.monthrange(year, month)[1]
                    for day in range(day, num_days):
                        d = date(year, month, day)
                        if record.is_scheduled(day=d):
                            preview_dates.append(str(d))

                        if len(preview_dates) >= 10:
                            break
                    if len(preview_dates) >= 10:
                        break

                    day = 1

                record.preview = ", ".join(preview_dates)
                continue

            for i in range(0, 400):
                d = today + relativedelta(days=i)
                if record.is_scheduled(day=d):
                    preview_dates.append(str(d))

                if len(preview_dates) >= 10:
                    break

            record.preview = ", ".join(preview_dates)

    @api.onchange("step")
    def _onchange_step(self):
        if self.step < 0:
            self.step = 0
            return {
                "warning": {
                    "title": "Warning",
                    "message": _("Value must be larger than 0"),
                },
            }
