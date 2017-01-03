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

    def _inactive_crons(self):
        crons = self.search([])
        if crons:
            vals = {'active': False, 'active_old': True}
            crons.write(vals)

    def _active_previous_crons(self):
        crons = self.with_context(active_test=False).search(
            [('active_old', '=', True)])
        if crons:
            crons.write({'active': True})


class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    def init(self):
        self.env['ir.cron']._inactive_crons()
        return super(IrModuleModule, self).init()

    def button_uninstall(self):
        self.env['ir.cron']._active_previous_crons()
        return super(IrModuleModule, self).button_uninstall()
