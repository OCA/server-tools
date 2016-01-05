# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Michael Viriyananda
#    2016
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

from lxml import etree
from openerp import models, fields, api


class WizardBaseCopyUserAccess(models.Model):
    _name = 'base.copy_user_access'
    _description = 'Wizard Copy User Access'

    user_id = fields.Many2one(
        string='User',
        comodel_name='res.users',
        required=True
        )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type='form', toolbar=False, submenu=False
    ):
        res = super(WizardBaseCopyUserAccess, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='user_id']"):
            active_ids = self._context.get('active_ids')
            domain = "[('id', 'not in', " + str(active_ids) + ")]"
            node.set('domain', domain)
        res['arch'] = etree.tostring(doc)
        return res

    def copy_access_right(self, cr, uid, ids, context=None):
        res = []
        obj_user = self.pool.get('res.users')

        record_id = context.get('active_ids')

        wizard = self.read(cr, uid, ids[0], context=context)

        user = obj_user.browse(cr, uid, wizard['user_id'][0])

        for group in user.groups_id:
            res.append(group.id)

        for data in record_id:
            user_id = obj_user.browse(cr, uid, data)
            vals = {
                'groups_id': [(6, 0, res)],
                }

            obj_user.write(cr, uid, [user_id.id], vals, context=context)

        return {'type': 'ir.actions.act_window_close'}
