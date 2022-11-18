# coding: utf-8
# Copyright (C) 2018 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import api, fields, models


_logger = logging.getLogger(__name__)


class IrCron(models.Model):
    _inherit = 'ir.cron'

    inactivity_period_ids = fields.One2many(
        comodel_name='ir.cron.inactivity.period', string='Inactivity Periods',
        inverse_name='cron_id')

    @api.model
    def _callback(self, model_name, method_name, args, job_id):
        job = self.browse(job_id)
        if any(job.inactivity_period_ids._check_inactivity_period()):
            _logger.info(
                "Job %s skipped during inactivity period",
                job.name)
            return
        return super(IrCron, self)._callback(
            model_name, method_name, args, job_id)
