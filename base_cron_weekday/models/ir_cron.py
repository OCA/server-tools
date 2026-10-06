# Copyright 2026 ForgeFlow
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from datetime import timedelta, timezone

from odoo import api, fields, models
from odoo.exceptions import ValidationError

WEEKDAY_FIELDS = [
    ("run_monday", 0),
    ("run_tuesday", 1),
    ("run_wednesday", 2),
    ("run_thursday", 3),
    ("run_friday", 4),
    ("run_saturday", 5),
    ("run_sunday", 6),
]


class IrCron(models.Model):
    _inherit = "ir.cron"

    run_monday = fields.Boolean(default=True)
    run_tuesday = fields.Boolean(default=True)
    run_wednesday = fields.Boolean(default=True)
    run_thursday = fields.Boolean(default=True)
    run_friday = fields.Boolean(default=True)
    run_saturday = fields.Boolean(default=True)
    run_sunday = fields.Boolean(default=True)

    @api.constrains(*[name for name, _weekday in WEEKDAY_FIELDS])
    def _check_run_weekdays(self):
        for cron in self:
            if not any(cron[name] for name, _weekday in WEEKDAY_FIELDS):
                raise ValidationError(
                    self.env._(
                        "A scheduled action must be allowed to run on at least "
                        "one weekday."
                    )
                )

    def _disallowed_weekdays(self):
        """Return the set of Python weekday numbers (Mon=0..Sun=6) the cron
        must not run on."""
        self.ensure_one()
        return {weekday for name, weekday in WEEKDAY_FIELDS if not self[name]}

    def _weekday_in_tz(self, nextcall):
        """Weekday of a naive-UTC ``nextcall`` evaluated in the cron's timezone."""
        return fields.Datetime.context_timestamp(self, nextcall).weekday()

    @api.model
    def _reschedule_later(self, job):
        super()._reschedule_later(job)
        cron = self.browse(job["id"])
        disallowed = cron._disallowed_weekdays()
        if not disallowed:
            return
        # core wrote nextcall via raw SQL, so drop the stale ORM value first.
        cron.invalidate_recordset(["nextcall"])
        nextcall = cron.nextcall
        # Defer one day at a time to the next allowed weekday, at the same time
        # of day. Bounded to at most 6 steps since at least one weekday is
        # always allowed.
        guard = 0
        while cron._weekday_in_tz(nextcall) in disallowed and guard < 7:
            nextcall = fields.Datetime.context_timestamp(cron, nextcall)
            nextcall += timedelta(days=1)
            nextcall = nextcall.astimezone(timezone.utc).replace(tzinfo=None)
            guard += 1
        if nextcall != cron.nextcall:
            self.env.cr.execute(
                "UPDATE ir_cron SET nextcall = %s WHERE id = %s",
                [nextcall, job["id"]],
            )
