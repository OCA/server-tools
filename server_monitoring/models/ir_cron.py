# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Alexandre Fayolle
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
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
