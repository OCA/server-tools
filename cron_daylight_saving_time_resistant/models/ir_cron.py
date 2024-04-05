# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime

import pytz

from odoo import api, fields, models

from odoo.addons.base.models.ir_cron import _intervalTypes

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = "ir.cron"

    daylight_saving_time_resistant = fields.Boolean(
        help="Adjust interval to run at the same hour after and before"
        "daylight saving time change. It's used twice a year"
    )

    def _calculate_daylight_offset(self, nextcall, delta, numbercall, now):

        tz = nextcall.tzinfo
        before_offset = tz.normalize(nextcall).utcoffset()

        while nextcall < now and numbercall:
            if numbercall > 0:
                numbercall -= 1
            if numbercall:
                nextcall += delta

        after_offset = tz.normalize(nextcall).utcoffset()

        diff_offset = after_offset - before_offset
        return diff_offset

    @classmethod
    def _process_job(cls, db, cron_cr, job):
        """Add or remove the Daylight saving offset when needed."""
        res = super()._process_job(db, cron_cr, job)
        # changing the date has to be after the super, else, e may add a hour
        # to next call, and the super will no run the cron, (because now will
        # be 1 hour too soon) and the date will just be incremented of 1
        # hour, each hour...until the changes time really occurs...
        if job["daylight_saving_time_resistant"]:
            with db.cursor() as job_cr:
                try:
                    cron = api.Environment(
                        job_cr,
                        job["user_id"],
                        {"lastcall": fields.Datetime.from_string(job["lastcall"])},
                    )[cls._name]
                    now = fields.Datetime.context_timestamp(cron, datetime.now())
                    # original nextcall
                    nextcall = fields.Datetime.context_timestamp(cron, job["nextcall"])
                    numbercall = job["numbercall"]
                    delta = _intervalTypes[job["interval_type"]](job["interval_number"])
                    diff_offset = cron._calculate_daylight_offset(
                        nextcall, delta, numbercall, now
                    )
                    if diff_offset and nextcall < now and numbercall:
                        cron_cr.execute(
                            """
                            SELECT nextcall FROM ir_cron WHERE id = %s
                        """,
                            (job["id"],),
                        )
                        res_sql = cron_cr.fetchall()
                        new_nextcall = res_sql and res_sql[0][0]
                        new_nextcall = fields.Datetime.context_timestamp(
                            cron, new_nextcall
                        )
                        new_nextcall -= diff_offset
                        modified_next_call = fields.Datetime.to_string(
                            new_nextcall.astimezone(pytz.UTC)
                        )
                        cron_cr.execute(
                            "UPDATE ir_cron SET nextcall=%s WHERE id=%s",
                            (modified_next_call, job["id"]),
                        )
                finally:
                    cron_cr.commit()
        return res
