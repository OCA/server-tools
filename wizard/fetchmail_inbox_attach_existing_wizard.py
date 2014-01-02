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

class FetchmailInboxAttachExistingWizard(TransientModel):
    _name = 'fetchmail.inbox.attach.existing.wizard'
    _description= 'Attach mail to existing object'

    _columns = {
            'res_model': fields.char('Model', size=128),
            'res_id': fields.integer('Object', required=True),
            'res_reference': fields.reference(
                'Reference',
                lambda self, cr, uid, context: [(m.model, m.name) for m in
                    self.pool.get('ir.model').browse(
                        cr, uid,
                        self.pool.get('ir.model').search(
                            cr, uid, [], context=context),
                        context)],
                None),
            'mail_id': fields.many2one('mail.message', 'Email', required=True),
    }

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        result = super(FetchmailInboxAttachExistingWizard, self)\
                .fields_view_get(
                        cr, user, view_id=view_id, view_type=view_type, 
                        context=context, toolbar=toolbar, submenu=submenu)
        if context and context.get('default_res_model'):
            result['fields']['res_id']['type'] = 'many2one'
            result['fields']['res_id']['relation'] = \
                    context['default_res_model']
            result['fields']['res_id']['context'] = {}
        return result

    def button_attach(self, cr, uid, ids, context=None):
        for this in self.browse(cr, uid, ids, context=context):
            if this.res_model and this.res_id:
                res_model = this.res_model
                res_id = this.res_id
            elif this.res_reference:
                res_model = this.res_reference._model._name
                res_id = this.res_reference.id
            else:
                raise except_orm(
                        _('Error'), _('You have to select an object!'))

            model = self.pool.get(res_model)
            if hasattr(model, 'message_update'):
                model.message_update(
                        cr, uid, [res_id], 
                        this.mail_id.fetchmail_inbox_to_msg_dict(),
                        context=dict(context, from_fetchmail_inbox=True))

            this.mail_id.fetchmail_inbox_move_to_record(res_model, res_id)

            return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model':
                        this.res_model or this.res_reference._model._name,
                    'res_id': this.res_id or this.res_reference.id,
                    }
