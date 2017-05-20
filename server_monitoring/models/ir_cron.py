# -*- coding: utf-8 -*-
# Author: Alexandre Fayolle
# Copyright 2014-2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, api


class IrCron(models.Model):
    _inherit = 'ir.cron'

    @api.model
    def _callback(self, model_name, method_name, args, job_id):
        super(IrCron, self)._callback(model_name,
                                      method_name,
                                      args,
                                      job_id)
        monitor_obj = self.env['server.monitor.process']
        monitor_obj.log_measure(model_name, method_name,
                                'cron job',
                                False, False)
