# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Thomas Rehn <thomas.rehn at initos.com>
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

from openerp.osv import osv
from email.Utils import COMMASPACE


class IrMailServer(osv.Model):
    _inherit = "ir.mail_server"

    def send_email(self, cr, uid, message, mail_server_id=None,
                   smtp_server=None, smtp_port=None, smtp_user=None,
                   smtp_password=None, smtp_encryption=None,
                   smtp_debug=False, context=None):

        "Add global bcc email addresses"

        # These are added here in send_email instead of build_email
        #  because build_email is independent from the database and does not
        #  have a cursor as parameter.

        ir_config_parameter = self.pool.get("ir.config_parameter")
        config_email_bcc = ir_config_parameter.get_param(cr, uid,
                                                         "mail.always_bcc_to")

        if config_email_bcc:
            config_email_bcc = config_email_bcc.encode('ascii')
            existing_bcc = []
            if message['Bcc']:
                existing_bcc.append(message['Bcc'])
                del message['Bcc']
            message['Bcc'] = COMMASPACE.join(
                existing_bcc + config_email_bcc.split(',')
            )

        return super(IrMailServer, self)\
            .send_email(cr, uid, message, mail_server_id, smtp_server,
                        smtp_port, smtp_user, smtp_password, smtp_encryption,
                        smtp_debug, context)
