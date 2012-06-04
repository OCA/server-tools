# -*- encoding: utf-8 -*-
#################################################################################
#
#    Scheduler error mailer module for OpenERP
#    Copyright (C) 2012 Akretion
#    @author: Sébastien Beau <sebastien.beau@akretion.com>
#    @author David Beal <bealdavid@gmail.com>
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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

from osv import osv, fields
from datetime import datetime


class ir_cron(osv.osv):
    _inherit = "ir.cron"

    _columns = {
        'email_template' : fields.many2one('email.template', 'E-mail template'),
    }


    def _handle_callback_exception(self, cr, uid, model, func, args, job_id, job_exception):

        res = super(ir_cron, self)._handle_callback_exception(cr, uid, model, func, args, job_id, job_exception)

        my_cron = self.browse(cr, uid, job_id)

        if my_cron.email_template.id:
            # we put the job_exception in context to be able to get it inside the mail template
            context = {'job_exception': job_exception}
            id_mail_messsage = self.pool.get('email.template').send_mail(cr, uid,
                my_cron.email_template.id, my_cron.id, force_send=True, context=context)

        return res
