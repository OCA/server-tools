# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
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
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.osv import orm
from openerp.tools.safe_eval import safe_eval


class IrActionsServer(orm.Model):

    _inherit = 'ir.actions.server'

    def merge_message(self, cr, uid, keystr, action, context=None):
        """
        Translate the message in the recipient's language
        """
        if context is None:
            context = {}

        # If the recipient is not found, take the admin user instead
        recipient = self.pool['res.users'].browse(
            cr, uid, uid, context=context)

        active_id = context.get('active_id')
        active_model = context.get('active_model')

        if active_id and active_model:
            obj_pool = self.pool[active_model]
            res = obj_pool.browse(
                cr, uid, active_id, context=context)

            # Get the address of destination of the action
            cxt = {
                'self': obj_pool,
                'object': res,
                'obj': res,
                'pool': self.pool,
                'time': time,
                'cr': cr,
                'context': dict(context),
                'uid': uid,
                'user': recipient,
            }

            try:
                address = safe_eval(str(action.email), cxt)
            except Exception:
                address = str(action.email)

            addresses = address if isinstance(
                address, (tuple, list)) else [address]

            # Get the partner related to the address
            partner_model = self.pool['res.partner']
            partner_ids = partner_model.search(cr, uid, [
                ('email', 'in', addresses),
            ], context=context)
            if partner_ids:
                recipient = partner_model.browse(
                    cr, uid, partner_ids[0], context=context)

        if recipient.lang:
            keystr = self.pool['ir.translation']._get_source(
                cr, uid, False, 'model', recipient.lang, keystr)

        return super(IrActionsServer, self).merge_message(
            cr, uid, keystr, action, context=context)
