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

        Returns a custom action built modifying the original one.
        """

        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        if context is None:
            context = {}

        # we expect one wizard instance at a time
        for wiz in self.browse(cr, uid, ids, context=context):
            action_id = mod_obj.get_object_reference(
                cr, uid, 'stock', 'action_production_lot_form')[1]
            action = act_obj.read(cr, uid, [action_id], context=context)[0]

            ctx = (
                "{'open_lot_by_attribute_set': True, "
                "'attribute_group_ids': %s}"
                % [
                    group.id
                    for group in wiz.attribute_set_id.attribute_group_ids
                ]
            )

            action['context'] = ctx
            action['domain'] = (
                "[('attribute_set_id', '=', %s)]"
                % wiz.attribute_set_id.id
            )
            action['name'] = wiz.attribute_set_id.name
            return action
