# -*- coding: utf-8 -*-
##############################################################################
#
#    This module uses OpenERP, Open Source Management Solution Framework.
#    Copyright (C):
#        2012-Today Serpent Consulting Services (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from openerp.osv import fields
from openerp.osv.orm import TransientModel
from openerp.tools.translate import _


class MassSortWizard(TransientModel):
    _name = 'mass.sort.wizard'

    def _default_description(self, cr, uid, context=None):
        config_obj = self.pool['mass.sort.config']
        config = config_obj.browse(
            cr, uid, context.get('mass_sort_config_id'), context=context)

        return _(
            "You will sort the field '%(field)s' for %(qty)d %(model)s(s)"
            ". \n\nThe sorting will be done by %(field_list)s.") % ({
                'field': config.one2many_field_id.field_description,
                'qty': len(context.get('active_ids', False)),
                'model': config.model_id.name,
                'field_list': ', '.join(
                    [x.field_id.field_description for x in config.line_ids])
                })

    _columns = {
        'description': fields.text(string='Description', readonly=True),
    }
    _defaults = {
        'description': _default_description,
    }

    def button_apply(self, cr, uid, ids, context=None):
        config_obj = self.pool['mass.sort.config']
        model_obj = self.pool[context.get('active_model')]
        active_ids = context.get('active_ids')
        config = config_obj.browse(
            cr, uid, context.get('mass_sort_config_id'), context=context)

        one2many_obj = self.pool[config.one2many_field_id.relation]
        parent_field = config.one2many_field_id.relation_field

        order_list = []
        for line in config.line_ids:
            order_list.append(
                line.desc and
                '%s desc' % line.field_id.name or line.field_id.name)
        order = ', '.join(order_list)

        for item in model_obj.browse(cr, uid, active_ids, context=context):
            # DB Query sort by the correct order
            line_ids = one2many_obj.search(
                cr, uid, [(parent_field, '=', item.id)], order=order,
                context=context)
            # Write new sequence to sort lines
            sequence = 1
            for id in line_ids:
                one2many_obj.write(
                    cr, uid, [id], {'sequence': sequence}, context=context)
                sequence += 1
        return {'type': 'ir.actions.act_window_close'}
