# -*- coding: utf-8 -*-
# © 2018 Akretion - Raphaël Reverdy
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import pytz
from datetime import datetime

from openerp import api, fields, models
from openerp.osv import fields as osv_fields
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.addons.base.ir.ir_cron import _intervalTypes
_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = "ir.cron"

    daylight_saving_time_resistant = fields.Boolean(
        help="Adjust interval to run at the same hour after and before"
        "daylight saving time change. It's used twice a year")

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

    def _process_job(cls, job_cr, job, cron_cr):
        """Add or remove the Daylight saving offset when needed."""
        super(IrCron, cls)._process_job(job_cr, job, cron_cr)
        # changing the date has to be after the super, else, e may add a hour
        # to next call, and the super will no run the cron, (because now will
        # be 1 hour too soon) and the date will just be incremented of 1
        # hour, each hour...until the changes time really occurs...
        # if need to test this, use freeze_gun lib.
        if job['daylight_saving_time_resistant']:
            with api.Environment.manage():
                now = osv_fields.datetime.context_timestamp(
                    job_cr, job['user_id'], datetime.now())
                nextcall = osv_fields.datetime.context_timestamp(
                    job_cr, job['user_id'],
                    datetime.strptime(
                        job['nextcall'],  # original nextcall
                        DEFAULT_SERVER_DATETIME_FORMAT)
                )
                numbercall = job['numbercall']
                delta = _intervalTypes[job['interval_type']](
                    job['interval_number'])
                diff_offset = cls._calculate_daylight_offset(
                    nextcall, delta, numbercall, now)
                if diff_offset and nextcall < now and numbercall:
                    cron_cr.execute("""
                        SELECT nextcall FROM ir_cron WHERE id = %s
                    """, (job['id'],))
                    res_sql = cron_cr.fetchall()
                    new_nextcall = res_sql and res_sql[0][0]
                    new_nextcall = osv_fields.datetime.context_timestamp(
                        job_cr, job['user_id'],
                        datetime.strptime(
                            new_nextcall,  # original nextcall
                            DEFAULT_SERVER_DATETIME_FORMAT)
                    )
                    new_nextcall -= diff_offset
                    modified_next_call = fields.Datetime.to_string(
                        new_nextcall.astimezone(pytz.UTC))
                    cron_cr.execute("UPDATE ir_cron SET nextcall=%s WHERE id=%s",
                        (modified_next_call, job['id']))
                    cron_cr.commit()
