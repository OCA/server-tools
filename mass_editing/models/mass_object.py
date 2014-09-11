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

from openerp import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


class MassObject(orm.Model):
    _name = "mass.object"

    _columns = {
        'name': fields.char("Name", size=64, required=True, select=1),
        'model_id': fields.many2one(
            'ir.model', 'Model', required=True, select=1),
        'field_ids': fields.many2many(
            'ir.model.fields', 'mass_field_rel', 'mass_id', 'field_id',
            'Fields'),
        'ref_ir_act_window': fields.many2one(
            'ir.actions.act_window', 'Sidebar Action', readonly=True,
            help="Sidebar action to make this template available on records \
                 of the related document model"),
        'ref_ir_value': fields.many2one(
            'ir.values', 'Sidebar Button', readonly=True,
            help="Sidebar button to open the sidebar action"),
        'model_ids': fields.many2many('ir.model', string='Model List')
    }

    _sql_constraints = [
        ('name_uniq', 'unique (name)', _('Name must be unique!')),
    ]

    def onchange_model_id(self, cr, uid, ids, model_id, context=None):
        if context is None:
            context = {}
        if not model_id:
            return {'value': {'model_ids': [(6, 0, [])]}}
        model_ids = [model_id]
        model_obj = self.pool['ir.model']
        active_model_obj = self.pool.get(model_obj.browse(
            cr, uid, model_id).model)
        if active_model_obj._inherits:
            for key, val in active_model_obj._inherits.items():
                found_model_ids = model_obj.search(
                    cr, uid, [('model', '=', key)], context=context)
                model_ids += found_model_ids
        return {'value': {'model_ids': [(6, 0, model_ids)]}}

    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool['ir.actions.act_window']
        ir_values_obj = self.pool['ir.values']
        for data in self.browse(cr, uid, ids, context=context):
            src_obj = data.model_id.model
            button_name = _('Mass Editing (%s)') % data.name
            vals['ref_ir_act_window'] = action_obj.create(cr, SUPERUSER_ID, {
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'mass.editing.wizard',
                'src_model': src_obj,
                'view_type': 'form',
                'context': "{'mass_editing_object' : %d}" % (data.id),
                'view_mode': 'form,tree',
                'target': 'new',
                'auto_refresh': 1,
                }, context)
            vals['ref_ir_value'] = ir_values_obj.create(cr, SUPERUSER_ID, {
                'name': button_name,
                'model': src_obj,
                'key2': 'client_action_multi',
                'value': (
                    "ir.actions.act_window,"
                    + str(vals['ref_ir_act_window'])),
                'object': True,
                }, context)
        self.write(cr, uid, ids, {
            'ref_ir_act_window': vals.get('ref_ir_act_window', False),
            'ref_ir_value': vals.get('ref_ir_value', False),
            }, context)
        return True

    def unlink_action(self, cr, uid, ids, context=None):
        for template in self.browse(cr, uid, ids, context=context):
            try:
                if template.ref_ir_act_window:
                    act_window_obj = self.pool['ir.actions.act_window']
                    act_window_obj.unlink(
                        cr, SUPERUSER_ID, [template.ref_ir_act_window.id],
                        context=context)
                if template.ref_ir_value:
                    ir_values_obj = self.pool['ir.values']
                    ir_values_obj.unlink(
                        cr, SUPERUSER_ID, template.ref_ir_value.id,
                        context=context)
            except:
                raise orm.except_orm(
                    _("Warning"),
                    _("Deletion of the action record failed."))
        return True

    def unlink(self, cr, uid, ids, context=None):
        self.unlink_action(cr, uid, ids, context=context)
        return super(MassObject, self).unlink(cr, uid, ids, context=context)

    def copy(self, cr, uid, record_id, default=None, context=None):
        if default is None:
            default = {}
        default.update({'name': '', 'field_ids': []})
        return super(MassObject, self).copy(
            cr, uid, record_id, default, context=context)
