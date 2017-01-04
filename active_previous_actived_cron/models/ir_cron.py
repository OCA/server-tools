# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools import config


PARAM = 'disable_cron_tasks'
KEEP_ALIVE_CRONS = (
    # here is xml id of crons
    'base.autovacuum_job',
)


class IrCron(models.Model):
    _inherit = 'ir.cron'

    active_old = fields.Boolean(
        string='Intial active state',
        help="State of the cron before 'Active Previous Active Cron' "
             "module installation.")

    def _inactive_crons(self):
        alive_crons = [self.env.ref(x).id for x in KEEP_ALIVE_CRONS]
        # some crons shouldn't be inactived
        crons = self.search([('id', 'not in', alive_crons)])
        vals = {'active': False, 'active_old': True}
        crons.write(vals)
        self.env['ir.config_parameter'].set_param(PARAM, True)

    def _active_previous_crons(self):
        crons = self.with_context(active_test=False).search(
            [('active_old', '=', True)])
        crons.write({'active': True})
        self.env['ir.config_parameter'].set_param(PARAM, False)

    @api.model
    def _callback(self, model_name, method_name, args, job_id):
        if config.get(PARAM):
            disable_cron = self.env['ir.config_parameter'].get_param(PARAM)
            if not disable_cron:
                self._inactive_crons()
        return super(IrCron, self)._callback(
            model_name, method_name, args, job_id)
