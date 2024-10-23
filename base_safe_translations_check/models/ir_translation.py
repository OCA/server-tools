# Copyright 2021 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.exceptions import ValidationError

from odoo.addons.queue_job.job import job


class IrTranslation(models.Model):
    _inherit = "ir.translation"

    @job(default_channel="root.check_translations")
    def jobify_check_constraints(self):
        """Process translations one by one, to make it easy to process."""
        if len(self) > 1:
            try:
                self[0].jobify_check_constraints()
            except ValidationError:  # if that failed, create a job to get it checked.
                self[0].with_delay().jobify_check_constraints()
            self[1:].with_delay().jobify_check_constraints()
        else:
            self._validate_fields(self._fields)
