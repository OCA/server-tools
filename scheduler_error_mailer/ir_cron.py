# -*- encoding: utf-8 -*-
#################################################################################
#                                                                               #
#    Model module for OpenERP                                                   #
#    Copyright (C) 2010 Sébastien BEAU <sebastien.beau@akretion.comr>           #
#                                                                               #
#    This program is free software: you can redistribute it and/or modify       #
#    it under the terms of the GNU Affero General Public License as             #
#    published by the Free Software Foundation, either version 3 of the         #
#    License, or (at your option) any later version.                            #
#                                                                               #
#    This program is distributed in the hope that it will be useful,            #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#    GNU Affero General Public License for more details.                        #
#                                                                               #
#    You should have received a copy of the GNU Affero General Public License   #
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.      #
#                                                                               #
#################################################################################

from osv import osv, fields
import netsvc


class ir_cron(osv.osv, netsvc.Agent):
    _inherit = "ir.cron"

    _columns = {
        'email_to' : fields.char('TO', size=256, help="If an error occure with this scheduler an email will be send"),
        'message' : fields.text('Message', help="If an error occure with this scheduler this message will be send via email"),
        'send_email' : fields.boolean('Active'),
        'email_account' : fields.many2one('poweremail.core_accounts', 'FROM')
    }

    def _handle_callback_exception(self, cr, uid, model, func, args, job_id, job_exception):
        res = super(ir_cron, self)._handle_callback_exception(cr, uid, model, func, args, job_id, job_exception)
        job = self.read(cr, uid, job_id, ['send_email', 'message', 'email_TO', 'email_account', 'name'])
        #TODO USE POWEREMAIL TEMPLATE
        if job['send_email']:
            addresses = {'To' : job['email_TO']}
            mail_obj = self.pool.get('poweremail.mailbox')
            id = mail_obj.create(cr, uid, {
                                            'pem_to' : job['email_TO'], 
                                            'pem_subject' : "OPENERP : error when excecuting scheduler " + job["name"], 
                                            'pem_body_text' : job['message'],
                                            'pem_account_id' : job['email_account'][0],
                                            'mail_type' : 'text/plain',
                                            'folder' : 'outbox',
                                            'state' :'na',
                                        })
            mail_obj.send_this_mail(cr, uid, [id])
        return res
ir_cron()

