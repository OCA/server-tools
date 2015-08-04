# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Laetitia Gangloff
#    Copyright (c) 2015 Acsone SA/NV (http://www.acsone.eu)
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class actions_server(orm.Model):
    _inherit = "ir.actions.server"

    def __init__(self, pool, cr):
        super(actions_server, self).__init__(pool, cr)
        # add state 'sql_export_email'
        new_state = ('sql_export_email', _('Export SQL data by email'))
        if new_state not in self._columns['state'].selection:
            self._columns['state'].selection.append(new_state)
        return

    _columns = {
        'sql_export_id': fields.many2one(
            'sql.export', string='SQL export', ondelete='restrict'),
    }

    def onchange_state(self, cr, uid, ids, state, context=None):
        res = {}
        if state == 'sql_export_email':
            # model is not used in this type of action, but it is a required
            # field, so set the model 'ir.actions.server'
            model = self.pool['ir.model'].search(
                cr, uid, [('model', '=', 'ir.actions.server')],
                context=context)
            res['value'] = {'model_id': model[0]}
        return res

    def run(self, cr, uid, ids, context=None):
        """
        If the state of an action is sql_export_email,
        get data related to the sql_export and send the result by email
        """
        for action in self.browse(cr, uid, ids, context):
            if action.state == 'sql_export_email':
                # get data to export
                res_id = self.pool['sql.export'].export_sql_query(
                    cr, uid, [action.sql_export_id.id],
                    context=context)['res_id']
                data = self.pool['sql.file.wizard'].browse(cr, uid, res_id,
                                                           context=context)
                if context is None:
                    context = {}
                # data is already encoded in base64
                context['encoded_base_64'] = True
                # Prepare a message with the exported data to send with the
                # template of the configuration
                self._send_email(
                    cr, uid, action, data['file_name'], data['file'],
                    context=context)
        return super(actions_server, self).run(cr, uid, ids, context=context)
