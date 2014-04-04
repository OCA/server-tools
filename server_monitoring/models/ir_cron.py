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
from openerp.osv import orm


class IrCron(orm.Model):
    _inherit = 'ir.cron'

    def _callback(self, cr, uid, model_name, method_name, args, job_id):
        super(IrCron, self)._callback(cr, uid,
                                      model_name,
                                      method_name,
                                      args,
                                      job_id)
        monitor_obj = self.pool['server.monitor.process']
        context = {}
        monitor_obj.log_measure(cr, uid,
                                model_name, method_name,
                                'cron job',
                                False, False, context)
