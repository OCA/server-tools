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
from openerp.osv.orm import TransientModel

class FetchmailInboxAttachExistingWizard(TransientModel):
    _inherit = 'fetchmail.inbox.attach.existing.wizard'

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        result = super(FetchmailInboxAttachExistingWizard, self)\
                .fields_view_get(
                        cr, user, view_id=view_id, view_type=view_type, 
                        context=context, toolbar=toolbar, submenu=submenu)
        if context and context.get('default_mail_id') and\
                context.get('default_res_model') == 'account.invoice':
            mail = self.pool.get('mail.message').browse(
                    cr, user, context.get('default_mail_id'), context=context)
            result['fields']['res_id']['domain'] = [
                ('type', 'in', ('in_invoice', 'in_refund'))]
            result['fields']['res_id']['options'] = '{"quick_create": false}'
            if mail.author_id:
                result['fields']['res_id']['context'].update(
                    search_default_partner_id=\
                        mail.author_id.commercial_partner_id.id)
        return result
