# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
