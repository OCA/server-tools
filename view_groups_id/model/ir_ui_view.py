# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>)
#
#    Code snippets from openobject-server 7.0
#                          (C) 2004-2012 OpenERP S.A. (<http://openerp.com>)
#
#
#    All Rights Reserved
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
from openerp.osv.orm import Model
from openerp.osv import fields
from openerp import SUPERUSER_ID


class ir_ui_view(Model):
    _inherit = 'ir.ui.view'

    _columns = {
            'groups_id': fields.many2many(
                'res.groups', 'ir_ui_view_group_rel', 'view_id', 'group_id',
                string='Groups', help="If this field is empty, the view "
                "applies to all users. Otherwise, the view applies to the "
                "users of those groups only."),
            }

    def get_inheriting_views_arch(self, cr, uid, view_id, model, context=None):
        user_groups = frozenset(self.pool.get('res.users').browse(
            cr, SUPERUSER_ID, uid, context).groups_id)

        view_ids = [v[1] for v in 
            super(ir_ui_view, self).get_inheriting_views_arch(
                cr, uid, view_id, model, context=context)]

        # filter views based on user groups
        return [(view.arch, view.id)
                for view in self.browse(cr, SUPERUSER_ID, view_ids, context)
                if not (view.groups_id and 
                    user_groups.isdisjoint(view.groups_id))]
