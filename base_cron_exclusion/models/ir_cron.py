# Copyright 2017-21 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = "ir.cron"

    @api.constrains("mutually_exclusive_cron_ids")
    def _check_auto_exclusion(self):
        for item in self:
            if item in item.mutually_exclusive_cron_ids:
                raise ValidationError(
                    _(
                        "You can not mutually exclude a scheduled actions with "
                        "itself."
                    )
                )

    mutually_exclusive_cron_ids = fields.Many2many(
        comodel_name="ir.cron",
        relation="ir_cron_exclusion",
        column1="ir_cron1_id",
        column2="ir_cron2_id",
        string="Mutually Exclusive Scheduled Actions",
    )

    @staticmethod
    def _lock_mutually_exclusive_cron(db, job_id):
        lock_cr = db.cursor()
        lock_cr.execute(
            """
            WITH Q1 AS (SELECT ir_cron2_id as cron_id FROM ir_cron_exclusion
                            WHERE ir_cron1_id=%s
                        UNION ALL
                        SELECT ir_cron1_id as cron_id FROM ir_cron_exclusion
                            WHERE ir_cron2_id=%s)
                SELECT * FROM Q1
                GROUP BY cron_id;""",
            (job_id, job_id),
        )
        locked_ids = tuple(row[0] for row in lock_cr.fetchall())
        if locked_ids:
            lock_cr.execute(
                """SELECT *
                               FROM ir_cron
                               WHERE numbercall != 0
                                  AND active
                                  AND id IN %s
                               FOR UPDATE NOWAIT""",
                (locked_ids,),
                log_exceptions=False,
            )
            lock_cr.fetchall()
        return lock_cr

    @classmethod
    def _process_job(cls, db, cron_cr, job):
        locked_crons = cls._lock_mutually_exclusive_cron(db, job["id"])
        try:
            res = super(IrCron, cls)._process_job(db, cron_cr, job)
        finally:
            locked_crons.close()
            _logger.debug("released blocks for cron job %s" % job["cron_name"])
        return res
