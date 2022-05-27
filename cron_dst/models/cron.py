# © 2022 initOS GmbH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, timedelta

import psycopg2
from pytz import timezone

import odoo
from odoo import api, fields, models

from odoo.addons.base.models.ir_cron import ir_cron
from odoo.addons.base.models.res_partner import _tz_get

_logger = logging.getLogger(__name__)


_original_function = ir_cron._process_jobs


class MonkeyCron(ir_cron):
    @classmethod
    def _process_jobs(cls, db_name):
        registry = odoo.registry(db_name)
        registry[cls._name]._adjust_to_dst(db_name)
        return _original_function(db_name)


ir_cron._process_jobs = MonkeyCron._process_jobs


class Cron(models.Model):
    _inherit = "ir.cron"

    dst_offset = fields.Integer()
    tz = fields.Selection(
        _tz_get,
        string="Timezone",
        default=lambda self: self._context.get("tz"),
        help="Timezone used for this cron job. Setting this will ensure a fixed time "
        "for execution despite Daylight Saving Time changes",
    )

    @api.onchange("tz")
    def _onchange_dst(self):
        if self.tz:
            now = timezone("UTC").localize(datetime.now())
            t = now.astimezone(timezone(self.tz))
            self.dst_offset = t.dst().seconds
        else:
            self.dst_offset = 0

    @classmethod
    def _adjust_to_dst(cls, db_name):
        db = odoo.sql_db.db_connect(db_name)

        with db.cursor() as cr:
            cr.execute("SELECT * FROM ir_cron WHERE tz IS NOT NULL")
            jobs = cr.dictfetchall()

        for job in jobs:
            lock_cr = db.cursor()
            try:
                lock_cr.execute(
                    "SELECT * FROM ir_cron WHERE id = %s",
                    (job["id"],),
                    log_exceptions=False,
                )

                job_cr = db.cursor()
                try:
                    with api.Environment.manage():
                        env = api.Environment(job_cr, job["user_id"], {})
                        cron = env[cls._name].browse(job["id"])
                        cron._adjust_job_to_dst()

                        job_cr.commit()
                finally:
                    job_cr.close()

            except psycopg2.OperationalError as e:
                if e.pgcode == "55P03":
                    continue
                raise
            finally:
                lock_cr.close()

    def _adjust_job_to_dst(self):
        self.ensure_one()
        if not self.tz:
            return

        now = timezone("UTC").localize(datetime.now())
        # Get tz from company or execution user
        t = now.astimezone(timezone(self.tz))
        dst_offset = t.dst().seconds

        if self.dst_offset != dst_offset:
            self.nextcall += timedelta(seconds=self.dst_offset - dst_offset)
            self.dst_offset = dst_offset
            _logger.info("Adjusted %s to DST", self)
