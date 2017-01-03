# coding: utf-8
# © 2017 David BEAL @ Akretion
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class IrCron(models.Model):
    _inherit = 'ir.cron'

    active_old = fields.Boolean(
        string='Intial active state',
        help="State of the cron before 'Active Previous Active Cron' "
             "module installation.")


class Module(models.Model):
    _inherit = 'ir.module.module'

    def init(self):
        crons = self.env['ir.cron'].search([])
        if crons:
            vals = {'active': False, 'active_old': True}
            crons.write(vals)

    def button_uninstall(self):
        cron_m = self.env['ir.cron']
        crons = cron_m.with_context(active_test=False).search(
            [('active_old', '=', True)])
        if crons:
            crons.write({'active': True})
        return super(Module, self).button_uninstall()
