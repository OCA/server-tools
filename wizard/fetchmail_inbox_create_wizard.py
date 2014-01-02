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
from openerp.osv.orm import TransientModel, except_orm
from openerp.osv import fields
from openerp.tools.translate import _

class FetchmailInboxCreateWizard(TransientModel):
    _name = 'fetchmail.inbox.create.wizard'
    _description = 'Create object from mail'

    _columns = {
            'model_id': fields.many2one('ir.model', 'Model', required=True),
            'mail_id': fields.many2one('mail.message', 'Email', required=True),
    }

    def button_create(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids, context=context):
            model = self.pool.get(this.model_id.model)

            if hasattr(model, 'message_new'):
                object_id = model.message_new(
                        cr, uid,
                        this.mail_id.fetchmail_inbox_to_msg_dict(),
                        context=dict(context, from_fetchmail_inbox=True))
            else:
                object_id = model.create(cr, uid, {}, context=context)

            this.mail_id.fetchmail_inbox_move_to_record(
                    this.model_id.model, object_id)

            return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': this.model_id.model,
                    'res_id': object_id,
                    }
