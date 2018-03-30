# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
import base64
from openerp.osv.orm import Model, browse_record
from openerp.osv import fields

class MailMessage(Model):
    _inherit = 'mail.message'

    def _needaction_count(self, cr, uid, dom, context=None):
        if dom == [('model', '=', 'fetchmail.inbox.invoice')]:
            return len(self.search(cr, uid, dom, context=context))
        return super(MailMessage, self)._needaction_count(
                cr, uid, dom, context=context)
