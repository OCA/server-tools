# Copyright 2026 Quartile (https://www.quartile.co)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class QueueJob(models.Model):
    _inherit = "queue.job"

    data_import_settled = fields.Boolean(
        readonly=True,
        help="Whether the unit this job imports has already been accounted for "
        "on its import log. A job that is requeued must not count twice.",
    )

    def write(self, vals):
        res = super().write(vals)
        if vals.get("state") == "failed":
            self._settle_failed_import_units()
        return res

    def _settle_failed_import_units(self):
        """Account for an import job that ended in failure.

        A failing job's transaction, and any error row it wrote, is rolled
        back before the failure is recorded; this runs in the environment that
        records it, which is the one that survives.
        """
        for job in self:
            if job.model_name != "data.import.log":
                continue
            log = job.records
            if len(log) != 1:
                continue
            if job.method_name == "_parse_file":
                # Never read, so there are no units to account for.
                if log.state == "pending":
                    log._fail_file(job.exc_info or "")
                continue
            if job.method_name != "_run_unit" or log.state != "processing":
                continue
            if job.data_import_settled:
                continue
            log._settle_failed_unit(job, job.kwargs.get("unit_key"), job.exc_info or "")
