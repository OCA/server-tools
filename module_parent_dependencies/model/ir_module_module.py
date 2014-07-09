# -*- encoding: utf-8 -*-
##############################################################################
#
#    Module - Parent Dependencies module for Odoo
#    Copyright (C) 2014 GRAP (http://www.grap.coop)
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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


class module(Model):
    _inherit = 'ir.module.module'

    # Field function Section
    def _get_all_parent_ids(
            self, cr, uid, ids, field_name, arg, context=None):
        res = self._get_direct_parent_ids(
            cr, uid, ids, field_name, arg, context=context)
        for id in ids:
            parent_ids = list(res[id])
            undirect_parent_ids = self._get_all_parent_ids(
                cr, uid, res[id], field_name, arg, context=context)
            for parent_id in parent_ids:
                res[id] += undirect_parent_ids[parent_id]
            res[id] = list(set(res[id]))
        return res

    def _get_direct_parent_ids(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        imd_obj = self.pool['ir.module.module.dependency']
        for imm in self.browse(cr, uid, ids, context=context):
            imd_ids = imd_obj.search(
                cr, uid, [('name', '=', imm.name)], context=context)
            tmp = imd_obj.read(
                cr, uid, imd_ids, ['module_id'], context=context)
            imm_ids = [x['module_id'][0] for x in tmp]
            # Select only non uninstalled module
            imm_ids = self.search(
                cr, uid, [
                    ('id', 'in', imm_ids),
                    ('state', 'not in', ['uninstalled', 'uninstallable'])],
                context=context)
            res[imm.id] = imm_ids
        return res

    # Column Section
    _columns = {
        'direct_parent_ids': fields.function(
            _get_direct_parent_ids, type='many2many',
            relation='ir.module.module', string='Direct Parent Modules'),
        'all_parent_ids': fields.function(
            _get_all_parent_ids, type='many2many',
            relation='ir.module.module',
            string='Direct and Indirect Parent Modules'),
    }
