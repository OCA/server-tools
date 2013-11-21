# -*- coding: utf-8 -*-
###############################################################################
#                                                                             #
#   Author: Leonardo Pistone <leonardo.pistone@camptocamp.com>                #
#   Copyright 2013 Camptocamp SA                                              #
#                                                                             #
#   This program is free software: you can redistribute it and/or modify      #
#   it under the terms of the GNU Affero General Public License as            #
#   published by the Free Software Foundation, either version 3 of the        #
#   License, or (at your option) any later version.                           #
#                                                                             #
#   This program is distributed in the hope that it will be useful,           #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
#   GNU Affero General Public License for more details.                       #
#                                                                             #
#   You should have received a copy of the GNU Affero General Public License  #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

from openerp.osv.orm import TransientModel
from osv import fields


class open_lot_by_attribute_set(TransientModel):
    _name = 'open.lot.by.attribute.set'
    _description = 'Wizard to open lots by attributes set'

    _columns = {
        'attribute_set_id': fields.many2one('attribute.set', 'Attribute Set'),
    }

    def open_lot_by_attribute(self, cr, uid, ids, context=None):
        """Opens a lot by attributes

        :param cr: the current row, from the database cursor,
        :param uid: the current user’s ID for security checks,
        :param ids: List of account chart’s IDs # TODO FIX docstring

        :return: dictionary of Lot list window for a given attributes set

        """
        assert len(ids) == 1
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        context = context or {}
        attribute_set = self.browse(
            cr, uid, ids[0], context=context
        ).attribute_set_id
        result = mod_obj.get_object_reference(
            cr, uid, 'stock', 'action_production_lot_form')
        id = result[1] if result else False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        grp_ids = self.pool.get('attribute.group').search(
            cr, uid, [('attribute_set_id', '=', attribute_set.id)])
        ctx = (
            "{'open_lot_by_attribute_set': %s, 'attribute_group_ids': %s}"
            % (True, grp_ids)
        )
        result['context'] = ctx
        result['domain'] = "[('attribute_set_id', '=', %s)]" % attribute_set.id
        result['name'] = attribute_set.name
        return result
