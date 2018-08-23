# Copyright (C) 2018 by Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class IrCron(models.Model):
    _inherit = 'ir.cron'

    oneshot = fields.Boolean(
        string='Single use',
        default=False,
    )

    @api.model
    def create(self, vals):
        if vals.get('oneshot'):
            # quite silent - fail loudly if vals['numbercall'] is given?
            vals['numbercall'] = 1
        return super(IrCron, self).create(vals)

    @classmethod
    def _process_job(cls, job_cr, job, cron_cr):
        res = super(IrCron, cls)._process_job(job_cr, job, cron_cr)
        try:
            with api.Environment.manage():
                cron = api.Environment(job_cr, job['user_id'], {})[cls._name]
                if job.get('oneshot'):
                    # log this?
                    cron.browse(job.get('id')).unlink()
        finally:
            job_cr.commit()
            cron_cr.commit()
        return res

    @api.model
    def schedule_oneshot(
            self, model=False, method=False, params=False, code=False):
        # XXX: still under construction.
        if not model:
            # generic case, use `base` cause we don't really care
            model = self.env.ref('base.model_base').id
        if not isinstance(model, str):
            model = model.id
        if method and not code:
            code = 'model.{method}'.format(**locals())
        oneshot_name_seq = self.env.ref('base_cron_oneshot.seq_oneshot_name')
        self.create({
            'name': 'Oneshot #{}'.format(oneshot_name_seq.next()),
            # TODO: retrieve actual ID of a model
            'model_id': model.id,
            'code': code,
        })
