# -*- coding: utf-8 -*-
##############################################################################
#
#    BizzAppDev
#    Copyright (C) 2004-TODAY bizzappdev(<http://www.bizzappdev.com>).
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
from openerp.tools import config
from openerp.tools.translate import _


class ir_mail_server(osv.osv):
    _inherit = "ir.mail_server"

    def get_mode(self, dbname):
        mode = config.get('develop', {}).get(dbname,
                                             False) and 'develop' or False
        mode = not mode and config.get('test',
                                       {}).get(dbname,
                                               False) and 'test' or mode
        return mode

    def send_email(self, cr, uid, message, mail_server_id=None,
                   smtp_server=None, smtp_port=None, smtp_user=None,
                   smtp_password=None, smtp_encryption=None, smtp_debug=False,
                   context=None):
        if self.get_mode(cr.dbname):
            raise osv.except_osv(
                _("OpenERP Mode"),
                _("You Can not Send Mail Because OpenERP is in "
                  "Test/Develop mode"))
        return super(ir_mail_server, self).send_email(
            cr, uid, message, mail_server_id=mail_server_id,
            smtp_server=smtp_server, smtp_port=smtp_port, smtp_user=smtp_user,
            smtp_password=smtp_password, smtp_encryption=smtp_encryption,
            smtp_debug=smtp_debug, context=None)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
