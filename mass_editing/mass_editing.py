# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2010-Today OpenERP SA (<http://www.openerp.com>)
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


from osv import fields, osv
from tools.translate import _
from lxml import etree
from openerp import tools

class ir_model_fields(osv.osv):
    _inherit = 'ir.model.fields'
    
    def search(self, cr, uid, args, offset=0, limit=0, order=None, context=None, count=False):
        res = super(ir_model_fields, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
        for domain in args:
            if domain[0]== 'model_id' and type(domain[2]) != list:
                res = self.search(cr, uid, [('model_id', 'in', map(int, domain[2][1:-1].split(',')))])
        return res
        
ir_model_fields()

class mass_object(osv.osv):
    _name = "mass.object"

    _columns = {
        'name' : fields.char("Name", size=64, required=True, select=1),
        'model_id' : fields.many2one('ir.model', 'Model', required=True, select=1),
        'field_ids' : fields.many2many('ir.model.fields', 'mass_field_rel', 'mass_id', 'field_id', 'Fields'),
        'ref_ir_act_window':fields.many2one('ir.actions.act_window', 'Sidebar action', readonly=True,
                                            help="Sidebar action to make this template available on records "
                                                 "of the related document model"),
        'ref_ir_value':fields.many2one('ir.values', 'Sidebar button', readonly=True,
                                       help="Sidebar button to open the sidebar action"),
        'model_list': fields.char('Model List', size=256)
    }
    
    def onchange_model(self, cr, uid, ids, model_id, context=None):
        if context is None: context = {}
        model_list = ""
        if model_id:
            model_obj = self.pool.get('ir.model')
            model_data = model_obj.browse(cr, uid, model_id)
            model_list = "[" + str(model_id) + ""
            active_model_obj = self.pool.get(model_data.model)
            if active_model_obj._inherits:
                for key, val in active_model_obj._inherits.items():
                    model_ids = model_obj.search(cr, uid, [('model', '=', key)])
                    if model_ids:
                        model_list += "," + str(model_ids[0]) + ""
            model_list += "]"
#            model_list = map(int, model_list[1:-1].split(','))
#            context['model_list'] = model_list
#            print 'context:::', context
        return {'value': {'model_list': model_list}}

    def create_action(self, cr, uid, ids, context=None):
        vals = {}
        action_obj = self.pool.get('ir.actions.act_window')
        data_obj = self.pool.get('ir.model.data')
        for data in self.browse(cr, uid, ids, context=context):
            src_obj = data.model_id.model
            button_name = _('Mass Editing (%s)') % data.name
            vals['ref_ir_act_window'] = action_obj.create(cr, uid, {
                 'name': button_name,
                 'type': 'ir.actions.act_window',
                 'res_model': 'mass.editing.wizard',
                 'src_model': src_obj,
                 'view_type': 'form',
                 'context': "{'mass_editing_object' : %d}" % (data.id),
                 'view_mode':'form,tree',
                 'target': 'new',
                 'auto_refresh':1
            }, context)
            vals['ref_ir_value'] = self.pool.get('ir.values').create(cr, uid, {
                 'name': button_name,
                 'model': src_obj,
                 'key2': 'client_action_multi',
                 'value': "ir.actions.act_window," + str(vals['ref_ir_act_window']),
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
                    self.pool.get('ir.actions.act_window').unlink(cr, uid, template.ref_ir_act_window.id, context)
                if template.ref_ir_value:
                    ir_values_obj = self.pool.get('ir.values')
                    ir_values_obj.unlink(cr, uid, template.ref_ir_value.id, context)
            except:
                raise osv.except_osv(_("Warning"), _("Deletion of the action record failed."))
        return True

mass_object()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
